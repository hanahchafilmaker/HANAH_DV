# 리팩토링 완료: main_gui.py를 컨트롤러 중심 구조로 재조립 (Zotero급 상용 UI)

## ✅ 달성 목표
1. **컨트롤러 중심 아키텍처**: UI ↔ 모델 간 명확한 분리
2. **Zotero급 3-Pane UI**: 문맥보기 / 각주목록 / 상세편집 패널
3. **UX 폴리시**: hover 효과, 선택 강조, 즉각적인 피드백, 키보드 네비게이션
4. **정보 밀도 계층화**: 좌측(문맥) ← 중앙(그리드) ← 우측(상세)
5. **상태 피드백 시스템**: 상태바를 통한 실시간 피드백

## 📁 최종 구조
```
app/
├─ core/
│  ├─ engine.py              # DOCX 처리 기능
│  └─ footnote_manager.py    # 매칭 로직 (�andidate 생성, 파싱)
├─ state/
│  └─ app_state.py           # 중앙 상태 (footnotes, selected_fn_id, match_results, candidates_cache)
├─ controllers/
│  └─ editor_controller.py   # 메인 컨트롤러 (로드, 선택, 적용, 저장/내보내기)
├─ ui/
│  ├─ layout.py              # 메인 윈도우, 툴바, 3-pane 레이아웃, 상태바, 키보드 단축키
│  ├─ styles.py              # ttkbootstrap 스타일 (flatly 테마 기반)
│  ├─ panels/
│  │  ├─ left_doc.py         # 좌측: 문서 컨텍스트 (읽기 전용, 선택 강조)
│  │  ├─ center_table.py     # 중앙: 각주 리스트 (Excel 스타일, 행 선택/hover 효과, 상태 표시)
│  │  ├─ right_editor.py     # 우측: 편집 패널 (원문, 편집 박스, 적용 버튼, 후보 카드 영역)
│  │  └─ candidate_panel.py  # 후보 카드 (Zotero-style hover/selection 효과)
│  └─ components/
│     ├─ card.py             # 범용 카드 UI 컴포넌트
│     ├─ searchbar.py        # 검색 바 (placeholder)
│     ├─ statusbar.py        # 하단 상태바 (피드백 메시지)
│     └─ toolbar.py          # 상단 툴바 (파일, 저장, 내보내기, 일괄 처리)
└─ main.py                   # 새로운 진입점
```

## 🌟 주요 개선 사항

### 1. 상태 관리 개선
- `app_state.py`에 다음과 추가:
  - `selected_fn_id`: 현재 선택된 각주 ID
  - `candidates_cache`: 각주별 후보 캐시 (성능 향상)
  - `match_results`: 각주별 매칭 결과
  - `update_footnotes_for_left_panel()`: 왼쪽 패널 동기화 메서드

### 2. 컨트롤러 역할 확장
- `editor_controller.py`:
  - **파일 관리**: `load_doc()`, `save_csv()`, `export_bibtex()`
  - **각주 선택**: `select_footnote()` (캐시 활용)
  - **후보 적용**: `apply_candidate()` (선택된 후보 적용)
  - **상태 피드백**: `set_status()`를 통한 상태바 업데이트 위임
  - **키보드 단축키 지원**을 위한 메서드 제공

### 3. UI 레이아웃 개선
- `layout.py`:
  - 실제 **PanedWindow** 사용 (ttkbootstrap.widgets.PanedWindow)
  - 3-pane 구조: 좌측(1) : 중앙(2) : 우측(3) 비율
  - **툴바**: 파일 열기, CSV 저장, BibTeX 내보내기, 일괄 매칭
  - **상태바**: 하단에 contextual 피드백 (예: "Loaded 120 footnotes", "Saved ✔")
  - **키보드 단축키**:
    - ↑↓: 각주 목록 이동
    - Enter: 후보 선택 (베스트 매치 또는 첫 번째 후보)
    - Ctrl+S: 적용/저장
    - 초기 포커스: 각주 테이블에 설정

### 4. 좌측 문서 패널 (`left_doc.py`)
- 문서 컨텍스트 보기 (읽기 전용)
- **선택 강조**: 선택된 각주에 `#e6f3ff` 배경 + 볼드 글꼴
- **정보 밀도**: 긴 각주는 100자 제한으로 표시
- **동기화**: 상태 변경을 통해 선택 상태 업데이트

### 5. 중앙 각주 테이블 (`center_table.py`)
- **Excel-like 그리드 뷰**: ID | 원문 요약 | 상태 | 참고문헌
- **행 선택 효과**: 선택된 행에 성공 스타일 적용
- **Hover 효과**: 행 위에 마우스 올릴 때 정보 스타일로 변경
- **즉시 업데이트**: 클릭 시 오른쪽 패널 즉시 갱신
- **상태 표시**: 각주별 매칭 상태 (⏳ 처리 중, ✅ 완료, ❓ 실패)
- **왼쪽-오른쪽 패널과 선택 동기화**

### 6. 우측 편집 패널 (`right_editor.py`)
- 원문 각주 표시 (읽기 전용 라벨)
- 편집 가능한 텍스트 박스 (높이 3줄)
- 적용 버튼 (명시적 저장 액션)
- 후보 카드 영역 (동적으로 생성)

### 7. 후보 카드 UI (`candidate_panel.py`)
- **Zotero-style 인터랙션**:
  - 기본 상태: `bootstyle="light"`
  - Hover 시: `bootstyle="info"` (강조된 파란색 테두리)
  - 선택 상태: `bootstyle="success"` (초록색 배경, 상태 유지)
- **확신도 표시**: 신뢰도 백분율 (예: "85.3%")
- **제목 래핑**: 길이가 긴 제목도 여러 줄로 표시
- **선택 즉시 반영**: 컨트롤러를 통한 상태 업데이트 ( UI → Controller → State → UI refresh)

### 8. 스타일 테마 (`styles.py`)
- `flatly` 테마 기반으로 일관된 상용 외관 제공
- 폰트: Segoe UI (Windows標準)
- 적절한 패딩과 간격으로 정보 밀도 조절
- 컴포넌트별 스타일 구분 (카드, 버튼, 라벨 등)

## 🔧 사용법
```bash
python main.py
```
1. **파일 열기** → 툴바의 "파일 열기" 또는 메뉴에서 DOCX 선택
2. **각주 선택** → 중앙 테이블에서 각주 클릭 또는 ↑↓ 키로 이동
3. **후보 검토** → 우측 패널에 후보 카드 표시 (호버 시 강조)
4. **후보 선택** → 후보 카드 클릭 또는 Enter 키 (선택된 후보는 초록색으로 유지)
5. **적용/저장** → 적용 버튼 클릭 또는 Ctrl+S
6. **내보내기** → 툴바의 "CSV 저장" 또는 "BibTeX 내보내기"

## 🚀 다음 단계 권고 사항
1. **실제 테스트**: 다양한 DOCX 파일로 엔드투엔드 워크플로 검증
2. **파일 지속성**: 현재 상태를 로컬 파일에 저장하고 복구하는 기능 구현
3. **고급 키보드 네비게이션**:
   - 후보 카드 간 좌우 이동 (←→)
   - 주요 후보 간 상하 이동
   - Tab 순서 최적화
4. **검색 기능 구현**: `searchbar.py`를 통한 각주 검색 (본문, 저자, 년도 등)
5. **성능 최적화**: 대량 각주(500개+)를 위한 가상 스크롤링 또는 페이지네이션
6. **테스트 및 문서화**: 단위 테스트 작성 및 사용자 가이드 제공

## 🎯 결과
이전 구조:
```
Tkinter 일체형 (main_gui.py)
UI + 로직 + 상태 혼합
위젯 직접 접근 및 수정
성능 이슈 (대량 각주 시 느림)
제한된 피드백 및 인터랙션
```

현재 구조:
```
MVC + Controller 아키텍처
Zotero-style 3-pane UI
명확한 관심사 분리로 인한 유지보수성 향상
상태 기반 선언적 UI 업데이트
풍부한 피드백 시스템 (hover, 선택, 상태바 메시지)
정보 밀도 계층화 (좌문맥 ← 중앙그물 → 우세부)
상용 툴 수준의 키보드 및 마우스 인터랙션
```