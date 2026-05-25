"""
Footnote management utilities for the thesis tool.
Extracts footnotes from .docx (via direct XML parsing), provides CSV template for editing,
and generates bibliography from the edited footnotes.
"""

import os
import csv
import pandas as pd
import zipfile
import xml.etree.ElementTree as ET
import re
import tempfile
import json
import difflib
import requests
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from functools import lru_cache
import logging
import unicodedata

# -------------------------
# 로깅 설정
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("paper_system.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Namespaces used in Word XML
NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}


def _get_xml_from_docx(docx_path, path_in_zip):
    """Extract raw XML bytes from a .docx (which is a zip archive)."""
    with zipfile.ZipFile(docx_path) as z:
        if path_in_zip not in z.namelist():
            return None
        return z.read(path_in_zip)


def extract_footnotes(docx_path):
    """
    Extract footnotes from a .docx file by parsing the XML directly.
    Returns a list of dicts with keys:
        - fn_id: the footnote's internal ID (string)
        - fn_text: the footnote's text content
        - fn_refs: list of reference IDs in the main document that point to this footnote
    """
    footnotes_xml = _get_xml_from_docx(docx_path, 'word/footnotes.xml')
    document_xml = _get_xml_from_docx(docx_path, 'word/document.xml')

    if footnotes_xml is None:
        # No footnotes part
        return []

    # Parse footnotes.xml
    try:
        ft_root = ET.fromstring(footnotes_xml)
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse footnotes.xml: {e}")

    # Build mapping from footnote ID to its text
    fn_elements = {}
    for footnote in ft_root.findall('.//w:footnote', NS):
        fid = footnote.get(f"{{{NS['w']}}}id")
        if fid is None:
            continue
        # Collect all text inside the footnote
        texts = []
        for t in footnote.findall('.//w:t', NS):
            if t.text:
                texts.append(t.text)
        fn_text = ''.join(texts).strip()
        fn_elements[fid] = {
            'fn_id': fid,
            'fn_text': fn_text,
            'fn_refs': []  # will fill from document.xml
        }

    if document_xml is None:
        # still return footnotes even if we can't find refs
        return list(fn_elements.values())

    # Parse document.xml to find footnote references
    try:
        doc_root = ET.fromstring(document_xml)
    except ET.ParseError as e:
        # If we can't parse, just return footnotes without refs
        return list(fn_elements.values())

    for ref in doc_root.findall('.//w:footnoteRef', NS):
        fid = ref.get(f"{{{NS['w']}}}id")
        if fid in fn_elements:
            fn_elements[fid]['fn_refs'].append(fid)

    # Convert to list, sorted by fn_id as integer if possible
    def try_int(s):
        try:
            return int(s)
        except ValueError:
            return s

    sorted_items = sorted(fn_elements.values(), key=lambda x: try_int(x['fn_id']))
    return sorted_items


def write_footnote_template(docx_path, csv_path):
    """
    Create a CSV template from the footnotes in docx_path.
    Columns: fn_num,fn_type,status,fn_text,matched_ref
    fn_type is left blank for user to fill (or we can guess).
    status left blank.
    matched_ref left blank for user to fill.
    """
    footnotes = extract_footnotes(docx_path)
    rows = []
    for i, fn in enumerate(footnotes, start=1):
        rows.append({
            'fn_num': i,
            'fn_type': '',  # user can fill: 출처, 설명주, 재인용, etc.
            'status': '',   # user fills with ✅ 매칭 etc.
            'fn_text': fn['fn_text'],
            'matched_ref': ''
        })
    # If no footnotes, still create header
    if not rows:
        rows = [{'fn_num': '', 'fn_type': '', 'status': '', 'fn_text': '', 'matched_ref': ''}]

    fieldnames = ['fn_num', 'fn_type', 'status', 'fn_text', 'matched_ref']
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_edited_footnotes(csv_path):
    """
    Read the edited CSV and return list of dicts with at least fn_text and matched_ref.
    Also returns original fn_num for ordering.
    """
    df = pd.read_csv(csv_path, dtype=str).fillna('')
    # Ensure required columns exist
    required = ['fn_num', 'fn_text', 'matched_ref', 'status']
    for col in required:
        if col not in df.columns:
            df[col] = ''
    # Keep only rows where status contains a check mark (✅) for bibliography
    mask = df['status'].str.contains('✅', na=False)
    bib_df = df[mask].copy()
    # Preserve original order by fn_num (convert to int where possible)
    def safe_int(x):
        try:
            return int(x)
        except:
            return 9999
    bib_df['_fn_num_int'] = bib_df['fn_num'].apply(safe_int)
    bib_df = bib_df.sort_values('_fn_num_int')
    # Drop helper column
    bib_df = bib_df.drop(columns=['_fn_num_int'])
    # Return list of dicts
    return bib_df[['fn_num', 'fn_text', 'matched_ref', 'status']].to_dict('records')


def generate_bibliography_from_edited(csv_path):
    """
    Generate a deduplicated bibliography list from the edited CSV.
    Returns list of formatted reference strings (matched_ref) in order of appearance.
    Deduplication 우선순위: DOI > ISBN > normalized title+author
    """
    records = read_edited_footnotes(csv_path)
    seen = set()  # ("DOI"|"ISBN"|"NORM", value) 튜플로 충돌 방지
    bibliography = []

    isbn_pattern = re.compile(
        r'(?:ISBN(?:-1[03])?[:\s]*)?(97[89][- ]?(?:\d[- ]?){9}\d|\d{9}[\dXx])'
    )

    def _normalize(s):
        """비교용 정규화: 소문자, 구두점 제거, 공백 단일화"""
        s = re.sub(r'[^\w\s]', '', s.lower())
        return re.sub(r'\s+', ' ', s).strip()

    for rec in records:
        ref = rec['matched_ref'].strip()
        if not ref:
            continue

        # 1. DOI 우선 (가장 신뢰할 수 있는 식별자)
        doi = rec.get('doi', '').strip().lower()
        if doi:
            key = ("DOI", doi)
            if key not in seen:
                seen.add(key)
                bibliography.append(ref)
            continue  # DOI 있으면 아래 fallback 불필요

        # 2. ISBN (도서류)
        isbn_match = isbn_pattern.search(ref)
        if isbn_match:
            isbn = re.sub(r'[^0-9X]', '', isbn_match.group(0).upper())
            key = ("ISBN", isbn)
            if key not in seen:
                seen.add(key)
                bibliography.append(ref)
            continue

        # 3. Normalized title+author fallback
        norm = _normalize(ref)
        key = ("NORM", norm)
        if norm and key not in seen:
            seen.add(key)
            bibliography.append(ref)

    logger.info(f"참고문헌 {len(bibliography)}건 생성 (원본 {len(records)}건에서 중복 제거)")
    return bibliography


def update_docx_with_bibliography(docx_path, bibliography, output_path):
    """
    Append a bibliography section to the end of the docx.
    Each entry as a normal paragraph.
    """
    try:
        from docx import Document
        doc = Document(docx_path)
        # Add a heading for bibliography
        heading = doc.add_paragraph()
        heading_run = heading.add_run('참고문헌')
        heading_run.bold = True
        heading_run.font.size = doc.styles['Normal'].font.size  # keep same size; could adjust
        heading.alignment = 0  # left align; could justify etc.
        # Add each bibliography entry
        for ref in bibliography:
            p = doc.add_paragraph(ref)
            # Optional: apply hanging indent etc. For simplicity, normal.
        doc.save(output_path)
    except Exception as e:
        raise ValueError(f"Failed to update DOCX with bibliography: {e}")


def clean_reference(fn_text):
    """
    각주 문자열을 정제하여 검색에 적합한 형태로 만듭니다.
    - raw: 원본 각주 텍스트
    - cleaned: 정제된 텍스트 (검색용)
    - author: 추정된 저자 (없으면 empty string)
    - title: 추정된 제목 (없으면 empty string)
    - year: 추정된 연도 (없으면 empty string)
    """
    if not fn_text or not isinstance(fn_text, str):
        return {
            "raw": fn_text or "",
            "cleaned": "",
            "author": "",
            "title": "",
            "year": ""
        }

    raw = fn_text.strip()
    # 기본 정제: 여러 공백을 하나로, 앞뒤 공백 제거
    cleaned = re.sub(r'\s+', ' ', raw).strip()

    # 따옴표 정규화
    cleaned = cleaned.replace('""', '"').replace("''", "'")

    # 연도 추출 (4자리 숫자, 1000-2029 사이)
    year_match = re.search(r'\b(1[0-9]{3}|2[0-2][0-9]{3})\b', cleaned)
    year = year_match.group(0) if year_match else ""

    # 간단한 제목 추정: 큰따옴표나 작은따옴표로 묶인 부분
    title_match = re.search(r'["\'](.*?)["\']', cleaned)
    title = title_match.group(1) if title_match else ""

    # 저자 추정: 제목 앞에 있는 패턴 (예: "저자. 제목." 또는 "저자, 제목")
    # 간단히, 제목 앞에 있는 단어들을 저자로 간주 (실제로는 더 복잡할 수 있음)
    author = ""
    if title:
        # 제목 앞부분을 저자로 간주 (및 구두점 제거)
        before_title = cleaned.split(title)[0].strip()
        # 구두점과 불필요한 단어 제거
        author = re.sub(r'[.,:;]+$', '', before_title).strip()
        # 일반적인 저자 아닌 단어 제거 (예: 'in', 'edited by' 등)
        stop_words = {'in', 'edited by', 'trans', 'vol', 'no', 'pp', 'p.'}
        author_parts = [part for part in author.split() if part.lower() not in stop_words]
        author = ' '.join(author_parts)

    # 제목이 없을 경우, 연도 앞부분을 제목으로 간주 (최소한의 fallback)
    if not title and year:
        # 연도 앞부분을 제목 후보로
        before_year = cleaned.split(year)[0].strip()
        # 구두점 제거 및 길이 제한
        title_candidate = re.sub(r'[.,:;]+$', '', before_year).strip()
        if len(title_candidate) > 10:  # 의미 있는 길이인지 확인
            title = title_candidate

    return {
        "raw": raw,
        "cleaned": cleaned,
        "author": author,
        "title": title,
        "year": year
    }


@lru_cache(maxsize=2048)
def query_crossref(cleaned_query):
    """
    Crossref REST API를 호출하여 메타데이터를 검색합니다.
    성공 시 Crossref item JSON을 반환하고, 실패 시 None을 반환합니다.
    결과는 lru_cache로 캐싱됩니다 (중복 API 호출 방지).
    """
    if not cleaned_query or not isinstance(cleaned_query, str):
        return None

    url = "https://api.crossref.org/works"
    params = {
        "query": cleaned_query,
        "rows": 3
    }
    headers = {
        "User-Agent": "PaperAutoGenerator/1.0 (mailto:user@example.com)"
    }

    logger.info(f"Crossref 쿼리: '{cleaned_query[:60]}'")
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "ok" and data.get("message", {}).get("items"):
            items = data["message"]["items"]
            if items:
                logger.debug(f"Crossref 결과 {len(items)}건 반환")
                return items[0]
        logger.warning(f"Crossref 결과 없음: '{cleaned_query[:60]}'")
        return None
    except requests.exceptions.RequestException as e:
        logger.warning(f"Crossref 네트워크 오류: {e}")
        return None
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        logger.error(f"Crossref 응답 파싱 실패: {e}")
        return None


def calculate_confidence(parsed_ref, crossref_item):
    """
    파싱된 참고문헌과 Crossref 항목 사이의 신뢰도를 계산합니다.
    0.0에서 1.0 사이의 float 값을 반환합니다.
    """
    if not parsed_ref or not crossref_item:
        return 0.0

    score = 0.0
    # 제목 유사도 (가중치 0.6)
    title_sim = 0.0
    parsed_title = parsed_ref.get("title", "").lower()
    crossref_title = ""
    if crossref_item.get("title"):
        # Crossref 제목은 리스트 형태일 수 있음
        title_list = crossref_item["title"]
        if isinstance(title_list, list) and title_list:
            crossref_title = title_list[0].lower()
        elif isinstance(title_list, str):
            crossref_title = title_list.lower()

    if parsed_title and crossref_title:
        title_sim = difflib.SequenceMatcher(None, parsed_title, crossref_title).ratio()
    score += 0.6 * title_sim

    # 저자 유사도 (가중치 0.3)
    author_sim = 0.0
    parsed_author = parsed_ref.get("author", "").lower()
    crossref_authors = crossref_item.get("author", [])
    crossref_author_str = ""
    if crossref_authors and isinstance(crossref_authors, list):
        # 첫 번째 저자의 성만 추출 (간단한 처리)
        first_author = crossref_authors[0]
        if isinstance(first_author, dict):
            # 가족명이 있는 경우
            family = first_author.get("family", "")
            given = first_author.get("given", "")
            if family and given:
                crossref_author_str = f"{family} {given}".lower()
            elif family:
                crossref_author_str = family.lower()
        elif isinstance(first_author, str):
            crossref_author_str = first_author.lower()

    if parsed_author and crossref_author_str:
        author_sim = difflib.SequenceMatcher(None, parsed_author, crossref_author_str).ratio()
    score += 0.3 * author_sim

    # 연도 일치 여부 (가중치 0.1)
    year_match = 0.0
    parsed_year = parsed_ref.get("year", "")
    crossref_year = ""
    if crossref_item.get("issued"):
        date_parts = crossref_item["issued"].get("date-parts", [[]])
        if date_parts and date_parts[0]:
            crossref_year = str(date_parts[0][0])  # 첫 번째 요소는 연도

    if parsed_year and crossref_year and parsed_year.isdigit() and crossref_year.isdigit():
        if parsed_year == crossref_year:
            year_match = 1.0
    score += 0.1 * year_match

    # 점수를 0.0과 1.0 사이로 clamp
    return max(0.0, min(1.0, score))


def auto_match_reference(fn_text):
    """
    각주 텍스트를 분석하여 Crossref에서 자동으로 참고문헌을 매칭합니다.
    성공 시 다음과 같은 딕셔너리를 반환합니다:
        {
            "matched_ref": "...",  # 매칭된 참고문헌 문자열 (Crossref에서 생성)
            "doi": "...",          # DOI
            "confidence": 0.92,    # 신뢰도 점수
            "source": "crossref",  # 출처
            "abstract": "..."      # 초록/요약 (optional)
        }
    실패 시 None을 반환합니다.
    """
    if not fn_text or not isinstance(fn_text, str):
        return None

    try:
        # 1. 각주 텍스트 정제
        parsed = clean_reference(fn_text)
        if not parsed or not parsed["cleaned"]:
            return None

        # 2. Crossref 쿼리 (정규화된 키로 캐시 적중률 향상)
        normalized_query = parsed["cleaned"].lower().strip()
        crossref_item = query_crossref(normalized_query)
        if not crossref_item:
            return None

        # 3. 신뢰도 계산
        confidence = calculate_confidence(parsed, crossref_item)
        # 신뢰도가 troppo 낮으면 무시 (임계값 0.5)
        if confidence < 0.5:
            logger.info(f"낮은 신뢰도 ({confidence:.2f}) — 매칭 제외: '{fn_text[:50]}'")
            return None

        # 4. 매칭된 참고문헌 문자열 생성 (간단한形式)
        # Crossref 항목에서 저자, 제목, 연도, 출판처 등을 조합
        authors = crossref_item.get("author", [])
        author_str = ""
        if authors and isinstance(authors, list):
            author_list = []
            for auth in authors[:2]:  # 최대 2명의 저자만 표시
                if isinstance(auth, dict):
                    family = auth.get("family", "")
                    given = auth.get("given", "")
                    if family and given:
                        author_list.append(f"{family} {given}")
                    elif family:
                        author_list.append(family)
                elif isinstance(auth, str):
                    author_list.append(auth)
            author_str = ", ".join(author_list)
            if len(authors) > 2:
                author_str += " et al."

        title_list = crossref_item.get("title", [])
        title_str = ""
        if title_list and isinstance(title_list, list) and title_list:
            title_str = title_list[0]
        elif isinstance(title_list, str):
            title_str = title_list

        # 연도 추출
        year_str = ""
        if crossref_item.get("issued"):
            date_parts = crossref_item["issued"].get("date-parts", [[]])
            if date_parts and date_parts[0]:
                year_str = str(date_parts[0][0])

        # 출판처 또는 저널 추출
        container_title = ""
        if crossref_item.get("container-title"):
            cont_list = crossref_item["container-title"]
            if isinstance(cont_list, list) and cont_list:
                container_title = cont_list[0]
            elif isinstance(cont_list, str):
                container_title = cont_list

        # 참고문헌 문자열 조합 (간단한形式)
        parts = []
        if author_str:
            parts.append(author_str)
        if title_str:
            parts.append(f'"{title_str}"')
        if container_title:
            parts.append(container_title)
        if year_str:
            parts.append(year_str)
        matched_ref = ". ".join([p for p in parts if p])

        # DOI 추출
        doi = crossref_item.get("DOI", "")

        # 초록/요약 추출 (있는 경우)
        abstract = ""
        if crossref_item.get("abstract"):
            # HTML 태그 제거 및 정리
            abstract_raw = crossref_item["abstract"]
            abstract = re.sub(r'<[^>]+>', '', abstract_raw)  # 간단한 HTML 태그 제거
            abstract = re.sub(r'\s+', ' ', abstract).strip()  # 다중 공백 제거

        return {
            "matched_ref": matched_ref,
            "doi": doi,
            "confidence": round(confidence, 2),
            "source": "crossref",
            "abstract": abstract
        }
    except Exception as e:
        # 예외 발생 시 조용히 fallback (None 반환)
        logger.error(f"auto_match_reference 실패: {e}")
        return None


def _escape_bibtex(text: str) -> str:
    """BibTeX 특수문자를 이스케이프합니다. Zotero/JabRef/LaTeX 호환성 보장."""
    if not text:
        return ""
    # Unicode NFC 정규화 (한국어 등 다국어 안정성)
    text = unicodedata.normalize("NFC", text)
    replacements = [
        ('\\', '\\textbackslash{}'),  # 반드시 첫 번째로 처리
        ('&',  '\\&'),
        ('%',  '\\%'),
        ('$',  '\\$'),
        ('#',  '\\#'),
        ('_',  '\\_'),
        ('{',  '\\{'),
        ('}',  '\\}'),
        ('~',  '\\textasciitilde{}'),
        ('^',  '\\textasciicircum{}'),
    ]
    for char, escape in replacements:
        text = text.replace(char, escape)
    return text


def bibliography_to_bibtex(entries):
    """
    참고문헌 항목 목록을 BibTeX 문자열로 변환합니다.
    entries: 각 항목은 다음과 같은 키를 가진 딕셔너리입니다:
        - author, title, year, journal, publisher, doi, 등
    반환: BibTeX 형식의 문자열
    """
    if not entries:
        return ""

    logger.info(f"BibTeX 생성 시작: {len(entries)}건")
    bibtex_lines = []
    for i, entry in enumerate(entries):
        # 항목 유형 판단 (간단히 article 또는 book으로 가정)
        entry_type = "article"
        if entry.get("journal") or entry.get("container-title"):
            entry_type = "article"
        elif entry.get("publisher") and not entry.get("journal"):
            entry_type = "book"
        else:
            entry_type = "misc"

        # 인용 키 생성 (저자성_연도 형식, 없으면 기본 형식)
        author = entry.get("author", "")
        year = entry.get("year", "")
        if author and year:
            # 저자 성 추출 (간단히 마지막 단어)
            last_name = author.split()[-1] if author.split() else "unknown"
            # 특수 문자 제거
            last_name = re.sub(r'[^\w]', '', last_name)
            cite_key = f"{last_name}{year}"
        else:
            cite_key = f"ref{i+1}"

        # 중복 인용 키 방지 (간단히 인덱스 추가)
        base_key = cite_key
        count = 1
        while any(cite_key == e.get("cite_key", "") for e in entries[:i]):  # 이미 처리된 항목과 비교
            cite_key = f"{base_key}{count}"
            count += 1

        bibtex_lines.append(f"@{entry_type}{{{cite_key},")

        fields = []
        if author:
            fields.append(f"  author = {{{_escape_bibtex(author)}}}")
        title = entry.get("title") or entry.get("container-title")
        if title:
            fields.append(f"  title = {{{_escape_bibtex(title)}}}")
        if year:
            fields.append(f"  year = {{{year}}}")
        journal = entry.get("journal") or entry.get("container-title")
        if journal and entry_type == "article":
            fields.append(f"  journal = {{{_escape_bibtex(journal)}}}")
        publisher = entry.get("publisher")
        if publisher and entry_type == "book":
            fields.append(f"  publisher = {{{_escape_bibtex(publisher)}}}")
        doi = entry.get("doi")
        if doi:
            fields.append(f"  doi = {{https://doi.org/{_escape_bibtex(doi)}}}")
        abstract = entry.get("abstract")
        if abstract:
            fields.append(f"  note = {{{_escape_bibtex(abstract)}}}")

        bibtex_lines.extend(fields)
        bibtex_lines.append("}")
        bibtex_lines.append("")  # 빈 줄 추가

    return "\n".join(bibtex_lines)


def save_bibtex_file(entries, output_path):
    """
    참고문헌 항목 목록을 BibTeX 파일로 저장합니다.
    entries: bibliography_to_bibtex에 전달할 항목 목록
    output_path: 저장할 파일 경로
    """
    try:
        bibtex_content = bibliography_to_bibtex(entries)
        if not bibtex_content:
            raise ValueError("No bibliography entries to save")

        # UTF-8로 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(bibtex_content)
        return True
    except Exception as e:
        print(f"Failed to save BibTeX file: {e}")
        return False