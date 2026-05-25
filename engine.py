import shutil
import os
import pandas as pd
from zipfile import ZipFile
from lxml import etree

from create_cover import create_cover
from create_approval import create_approval

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = f"{{{W}}}"


# -------------------------
# 스타일 적용
# -------------------------
def update_style(tree, style_id, size):
    for style in tree.findall(f".//{NS}style"):
        if style.get(f"{NS}styleId") == style_id:
            rpr = style.find(f"{NS}rPr") or etree.SubElement(style, f"{NS}rPr")

            sz = etree.SubElement(rpr, f"{NS}sz")
            sz.set(f"{NS}val", str(size))


# -------------------------
# 문단 자동 스타일 적용
# -------------------------
def classify(text):
    if text.startswith("제") and "장" in text:
        return "Heading1"
    elif text.startswith("제") and "절" in text:
        return "Heading2"
    elif text.strip().startswith(tuple(str(i) + "." for i in range(10))):
        return "Heading3"
    return "Normal"


def apply_paragraph_styles(tree):
    for p in tree.findall(f".//{NS}p"):
        texts = p.findall(f".//{NS}t")
        if not texts:
            continue

        full = "".join([t.text for t in texts if t.text])
        style = classify(full)

        pPr = p.find(f"{NS}pPr") or etree.SubElement(p, f"{NS}pPr")
        pStyle = etree.SubElement(pPr, f"{NS}pStyle")
        pStyle.set(f"{NS}val", style)


# -------------------------
# 참고문헌 생성
# -------------------------
def extract_references():
    df = pd.read_csv("각주_참고문헌_매칭표.csv")
    refs = df[df["status"].str.contains("✅")]["matched_ref"]

    refs = list(set(refs.dropna()))
    return refs


# -------------------------
# docx 처리
# -------------------------
def process_docx(input_file, output_file):
    temp = "temp"

    if os.path.exists(temp):
        shutil.rmtree(temp)
    os.mkdir(temp)

    with ZipFile(input_file, 'r') as zip_ref:
        zip_ref.extractall(temp)

    # styles
    styles_path = os.path.join(temp, "word", "styles.xml")
    tree = etree.parse(styles_path)

    update_style(tree, "Normal", 22)
    update_style(tree, "Heading1", 32)
    update_style(tree, "Heading2", 28)

    tree.write(styles_path)

    # document
    doc_path = os.path.join(temp, "word", "document.xml")
    doc_tree = etree.parse(doc_path)

    apply_paragraph_styles(doc_tree)

    doc_tree.write(doc_path)

    # 다시 압축
    with ZipFile(output_file, 'w') as docx:
        for root, _, files in os.walk(temp):
            for file in files:
                path = os.path.join(root, file)
                docx.write(path, os.path.relpath(path, temp))

    shutil.rmtree(temp)


# -------------------------
# 전체 실행
# -------------------------
def process_all(input_file):

    # 1. 본문 정리
    processed_doc = "본문_정리.docx"
    process_docx(input_file, processed_doc)

    # 2. 표지
    create_cover()

    # 3. 인준지
    create_approval()

    # 4. 참고문헌
    refs = extract_references()

    with open("참고문헌.txt", "w", encoding="utf-8") as f:
        for r in refs:
            f.write(r + "\n")

    print("✅ 전체 논문 생성 완료")