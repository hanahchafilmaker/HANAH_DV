# 논문 교정기 - Manual Footnote Editor 구현 완료 요약

## 구현 완료 사항

### 1. 아키텍처 전면 개편 (`footnote_manager.py`, `main_gui.py`)
- Crossref API 완전 제거
- 자동 매칭 시스템 제거 (MatchCandidate, MatchResult, scoring engine)
- 스레드 기반 작업자 제거 (더 이상 백그라운드 처리 불필요)
- UI 레지스트리 및 팩토리 패턴 제거
- 단순 파서 기반 지역 추출만 유지

### 2. 핵심 구성 요소
#### 데이터 모델 (`footnote_manager.py`)
- `Footnote` 데이터클래스: fn_id, fn_text, author, title, year, pages, publisher, location
- 순수 지역 파서 (`parse_footnote_text`): 연도 추출 및 기본 휴리스틱 파싱
- 참고문헌 서식 함수: APA, Chicago, MLA 스타일 지원

#### UI (`main_gui.py`)
- 엑셀 스타일 편집 UI (Treeview 기반)
- 더블클릭으로 셀 편집 가능 (inline editing)
- 실시간 상태 업데이트 (편집 시 즉시 반영)
- 인용 스타일 선택 콤보박스 (APA/Chicago/MLA)
- 단축 인용 모드 토글 버튼
- Word 내보내기 버튼

#### 내보내기 기능
- 선택된 인용 스타일에 따라 참고문헌 생성
- Microsoft Word (.docx) 형식으로 저장
- 각 참고문헌에 번호付 항목 생성

### 3. 워크플로우
1. DOCX 파일 로드 → 각주 추출
2. 추출된 각주를 편집 가능한 표에 표시
3. 사용자가 직접 각 필드(author, title, year, 등) 수정
4. 인용 스타일 및 단축/전체 인용 모드 선택
5. "Word 내보내기" 클릭 → formatted bibliography 생성 및 저장

### 4. 주요 장점
- **완전 로컬**: 외부 API 의존성 없음 (Crossref, OpenLibrary 등)
- **스레드 안전성**: 백그라운드 처리 제거로 모든 UI 작업 메인스레드에서 실행
- **직관적인 UX**: 엑셀처럼 바로 편집 가능한 인터페이스
- **명확한 책임 분리**: 
  - 파서: 텍스트 → 기본 구조 변환 (순수 함수)
  - UI: 사용자 입력 및 표시 담당
  - 포매터: 구조 → 인용 문자열 변환
  - 내보내기: 최종 출력 생성
- **확장 용이함**: 새로운 인용 스타일 추가 시 포매터 함수만 추가하면 됨
- **안정성**: 복잡한 로직 제거로 오류 가능성 현저히 감소

### 5. 제거된 컴포넌트
- `auto_match_reference()` 함수
- Crossref API 레이어 (`query_crossref`, `format_reference_from_crossref`)
- 매칭 후보 시스템 (`MatchCandidate`, `MatchResult`)
- 점수 엔진 (`_calculate_similarity_score`, confidence 계산)
- citation memory 시스템
- 스레드 워커 (`_process_all_footnotes_matching`)
- UI 디스패처 루프 (`_ui_dispatch_loop`, `_handle_ui_message`)
- UI 레지스트리 (`ui_registry`)
- UI 팩토리 (`UIFactory`)
- 후보 표시/토글 UI
- 신뢰도 표시 UI

### 6. 유지된 컴포넌트
- 각주 추출 핵심 (`extract_footnotes` via XML 파싱)
- 발문서 생성 기능 (`update_docx_with_bibliography`)
- CSV 템플릿 생성/읽기 함수
- 기본 텍스트 정제 기능
- 문서 스타일 적용 엔진 (`engine.process_docx`)

## 사용 예시
1. `DOCX 파일 선택` 버튼으로 파일 로드
2. 각주가 표에 표시됨 (Author, Title, Year, Pages 열)
3. 표에서 더블클릭해서 필드 직접 편집 가능
4. 하단에서 인용 스타일 선택 (APA/Chicago/MLA)
5. 필요에 따라 "단축 인용 모드" 토글
6. `Word 내보내기` 클릭 → 저장 위치 선택 → formatted bibliography가 포함된 Word 문서 생성

## 기술적 주의사항
- 현재 파서는 간단한 휴리스틱 기반이므로 복잡한 인용 형례는 수동 수정이 필요함
- 향후 더 정교한 파서 라이브러리 통합 가능 (예: citeproc-py, référentiel)
- Word 내보내기는 python-docx 라이브러리 의존함
- 모든 핵심 로직은 단일 스레드에서 실행되어 thread safety 이슈 없음

## 예상 효과
- 처리 속도 향상 (외부 API 호출 제거)
- 오류율 감소 (네트워크 의존성 제거)
- 사용자 제어 증가 (모든 필드 직접 편집 가능)
- 학문적 워크플로우 적합성 (사용자가 최종 인용 형식 결정)
- 유지보수 용이함 (코드 복잡도 현저히 감소)