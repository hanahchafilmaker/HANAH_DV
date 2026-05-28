# Paper Citation Studio - EXE Build Instructions

## Overview
This application has been refactored to a controller-centered MVC architecture with Zotero-style 3-pane UI, featuring scroll synchronization and full keyboard navigation.

## ✅ Completed Enhancements
1. **Scroll Synchronization**: Left document panel and center table panel scroll together
2. **Keyboard Navigation**:
   - ↑↓ arrows: Navigate footnote list in center panel
   - Enter: Select best candidate for current footnote
   - Ctrl+S: Apply selected candidate
3. **UI Features**: Hover effects, selection highlighting, status bar feedback
4. **Import Fixes**: Resolved PyInstaller compatibility issues

## 📦 Building the EXE

### Prerequisites
1. Activate your virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
2. Install PyInstaller:
   ```powershell
   pip install pyinstaller
   ```

### Build Command
Run this from the project root (`C:\Users\botto\Desktop\논문_교정기`):

```powershell
pyinstaller --noconfirm --clean --windowed `
--name PaperCitationStudio `
--add-data "app;app" `
--hidden-import=app.core.footnote_manager `
--hidden-import=app.core.engine `
--hidden-import=app.ui.panels.candidate_card `
--hidden-import=lxml `
--hidden-import=ttkbootstrap `
main.py
```

### Expected Output
After building, find the EXE at:
```
dist\PaperCitationStudio\PaperCitationStudio.exe
```

## 🧪 Testing Checklist
After building and running the EXE, verify:
- [ ] Application launches with 3-pane UI
- [ ] Scroll synchronization works between panels
- [ ] ↑↓ arrow keys navigate footnote list
- [ ] Enter key selects best candidate
- [ ] Ctrl+S applies selected candidate
- [ ] File operations work (Open CSV, Save CSV, Export BibTeX)
- [ ] Candidate cards show hover/selection effects
- [ ] Status bar shows appropriate feedback

## 📁 Files Modified
- `app/controllers/editor_controller.py` - Fixed imports
- `app/core/__init__.py` - Added submodule exports
- `app/ui/panels/right_editor.py` - Fixed candidate card import
- `app/ui/panels/left_doc.py` - Added scroll synchronization
- `app/ui/panels/center_table.py` - Added scroll sync + keyboard nav
- `app/ui/layout.py` - Coordinated scroll synchronization

## 🎯 Result
You now have a standalone Windows executable that users can run without needing Python installed, featuring a polished Zotero-style interface for managing footnote citations in DOCX documents.