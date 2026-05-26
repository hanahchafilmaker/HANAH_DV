# 논문 교정기 - Citation Memory 시스템 구현 완료 요약

## 구현 완료 사항

### 1. Citation Memory 구조 추가 (`footnote_manager.py`)
- `citation_memory` 전역 변수 추가: 순차적 citation 추적을 위한 저장소
- `reset_citation_memory()` 함수: 문서 처리 시 메모리 초기화
- `normalize_key()` 함수: 저자 + 제목 기준 정규화 키 생성
- `looks_like_full_citation()` 함수: 출판사, 연도, DOI 등으로 full citation 판별
- `looks_like_short_citation()` 함수: 페이지番号 끝남으로 short citation 판별

### 2. 자동 매칭 로직 개선 (`footnote_manager.py`)
- `auto_match_reference()` 함수 완전 리팩토링:
  1. citation memory에서 먼저 반복 citation 확인
  2. short citation인 경우 이전 full citation과 연결
  3. full citation인 경우 메모리에 저장하고 Crossref로 enrichment
  4. Crossref는 메타데이터 공급 역할만 수행 (fallback)
- `build_query()` 함수 추가: title + author + year로 검색 쿼리 구성
- `format_reference_from_crossref()` 함수 추가: Crossref 결과로부터 reference 문자열 생성

### 3. GUI 개선 (`main_gui.py`)
- 단일 작업자 스레드 사용: `_process_all_footnotes_matching()`로 순차 처리
- citation type 표시 추가: UI에 "유형" 컬럼 추가 ([FULL], [REPEATED], [SHORT] 등)
- 스레드 안전 UI 업데이트: `_update_auto_match_ui_threadsafe()` 함수
- flake number 줄 무시: 추출 시 `[1]`, `[2]` 같은 줄을 무시하도록 수정

### 4. 신뢰도 조정
- 메모리 기반 매칭: 0.95 신뢰도 (매우 높음)
- Crossref enrichment: 0.90 신뢰도
- 자동 채우기 임계값: 0.70 유지

## 다음 단계 (권장 사항)

### 향후 개선할 사항
1. **후보 3개 추천 구조**: 현재는 단일 매칭만 반환하나, 상위 3개 후보를 반환하도록 개선
2. **정확한 작성자 추출**: Crossref 저자 데이터 구조 개선 처리
3. **다양한 citation 스타일 지원**: Chicago, APA, MLA 등 구체적 형식에 맞는 처리
4. **사용자 피드백 루프**: 사용자가 매칭을 수정하면 해당 정보를 메모리에 반영
5. **다중 소스 fallback**: Crossref 실패 시 OpenLibrary, Semantic Scholar 등으로 확장

### 현재 구현의 장점
- **Race condition eliminated**: 순차 처리로 citation memory 일관성 보장
- **의미있는 매칭**: 문장 전체 검색이 아닌 제목+저자+년도로 검색
- **반복 citation 자동 처리**: 학술 문서의 핵심 워크플로우 정확히 구현
- **점진적 enrichment**: 먼저 메모리 구축 후 Crossref로 메타데이터 보강

이 구현으로 이제 논문 각주 시스템은 단순한 "참고문헌 매칭기"가 아니라 actual academic citation workflow를 따른 "반복 citation 추적 시스템"으로 동작합니다.