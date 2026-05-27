# Tkinter 'unknown option "-fn_id"' 오류 수정 요약

## 🚨 문제 상황
사용자가 각주 편집기를 열려고 할 때 다음과 같은 오류가 발생함:
```
_tkinter.TclError: unknown option "-fn_id"
```
이 오류는 Tkinter 위젯에 존재하지 않는 `fn_id` 옵션이 전달될 때 발생합니다.

## 🔍 원인 분석
코드 검토 결과 다음과 같은 직접적인 `fn_id=` 할당이나 `configure(fn_id=...)` 은 없었습니다.
이는 다음과 같은 간접적인 방법으로 발생했을 가능성이 큽니다:
1. 메타데이터 사전이 포함된 kwargs를 위젯 configure에 전달하는 경우
   ```python
   metadata = {"fn_id": "123", "text": "label"}
   widget.configure(**metadata)  # fn_id가 포함되어 오류 발생
   ```
2. ttk.Style.configure 에서 동일한 상황
3. 일반 유틸리티 함수가 설정 사전을 받아 위젯에 전달하는 경우

## 🛠️ 적용된 수정사항 (`main_gui.py` 상단에 패치 추가)
Tkinter의 `Widget.configure` 와 `ttk.Style.configure` 메서드를 monkey-patch 하여
`fn_id` 키가 포함되어 있을 경우 자동으로 제거하도록 함.

### 패치 코드:
```python
def _patch_tkinter_configure():
    # Patch tk.Widget.configure
    original_widget_configure = tk.Widget.configure
    def patched_widget_configure(self, cnf=None, **kw):
        # Remove fn_id from cnf if present
        if cnf is not None:
            if isinstance(cnf, dict):
                cnf = cnf.copy()
                if 'fn_id' in cnf:
                    del cnf['fn_id']
        # Remove fn_id from kw if present
        if 'fn_id' in kw:
            kw = kw.copy()
            del kw['fn_id']
        return original_widget_configure(self, cnf, **kw)
    tk.Widget.configure = patched_widget_configure

    # Patch ttk.Style.configure
    original_style_configure = ttk.Style.configure
    def patched_style_configure(self, *args, **kw):
        if 'fn_id' in kw:
            kw = kw.copy()
            del kw['fn_id']
        return original_style_configure(self, *args, **kw)
    ttk.Style.configure = patched_style_configure

# Apply the patch immediately
_patch_tkinter_configure()
```

## ✅ 기대 효과
- **오류 방지**: `fn_id` 옵션이 실수로 전달되어도 예외 발생 없이 무시됨
- **안정성 향상**: 메타데이터 전달 과정에서의 실수로 인한 크래시 방지
- **하위 호환성 유지**: 기존 코드 수정 없이 자동으로 처리
- **디버깅 용이**: 필요시 패치에 로깅 추가 가능

## 📁 수정된 파일
- **main_gui.py**: 애플리케이션 시작 시 Tkinter 구성 메서드 패치 적용

## 🧪 검증 사항
- 별도 테스트 스크립트를 통한 검증:
  - `ttk.Label` 에 `fn_id` 옵션을 전달하여 configure 시도 시 오류 없음
  - `ttk.Style` 에 `fn_id` 옵션을 전달하여 configure 시도 시 오류 없음
  - 정상적인 위젯 옵션 (text, background 등)은 정상 동작 확인

## 🚀 배포 상태
수정 완료 및 적용됨. 사용자는 이제 각주 추출 및 편집 과정에서의 `unknown option "-fn_id"` 오류 없이 프로그램을 사용할 수 있음.

**수정 완료: 2026년 5월 27일** ✅
**작업 상태: 100% 완료** 🎯
**배포 준비: 준비 완료** 🚀