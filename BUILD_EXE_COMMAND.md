# EXE Build Command for Paper Citation Studio

## PyInstaller Command (Run in Project Root)

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

## Explanation

- `--noconfirm`: Replace output directory without asking
- `--clean`: Clean PyInstaller cache before building
- `--windowed`: No console window (GUI application)
- `--name PaperCitationStudio`: Name of the EXE file
- `--add-data "app;app"`: Include the app directory
- Hidden imports: Ensure specific modules are included (critical for PyInstaller)
- `main.py`: Entry point

## Expected Output Structure
```
dist/
 └─ PaperCitationStudio/
     ├─ PaperCitationStudio.exe
     ├─ app/
     │   ├─ core/
     │   ├─ state/
     │   ├─ controllers/
     │   └─ ui/
     └─ _internal/
```

## Testing Checklist After Build
- [ ] Application launches with 3-pane UI
- [ ] Scroll synchronization works between panels
- [ ] ↑↓ arrow keys navigate footnote list
- [ ] Enter key selects best candidate
- [ ] Ctrl+S applies selected candidate
- [ ] File operations work (Open, Save CSV, Export BibTeX)
- [ ] Candidate cards show hover/selection effects
- [ ] Status bar shows appropriate feedback