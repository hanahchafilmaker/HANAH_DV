# 논문 교정기 - Top-3 Candidate System

## Overview
This implementation adds a Top-3 Candidate System to the thesis tool, allowing users to select from multiple reasonable citation options rather than being forced into an automatic selection.

## Features

### For Users
- **REPEATED Citations**: Automatically resolved with high confidence (no selection needed)
- **FULL Citations**: Shows top 3 candidate matches in expandable section below each footnote row
- **Candidate Information**: Each candidate shows preview text, confidence percentage, and source (memory/local)
- **Easy Selection**: Click a candidate to instantly replace the current matched reference
- **Visual Indication**: DOI labels are clickable and show popup details

### Technical Implementation
- **Memory-First Flow**: SHORT → memory repeat detection → FULL processing
- **Smart Scoring**: Weighted similarity based on title (0.4), author (0.4), year (0.2)
- **Local Variations**: Generates multiple candidate formats from parsed data
- **Thread Safety**: All UI updates occur on main thread via queue-based dispatcher
- **Backward Compatibility**: Maintains existing functionality and data structures

## Files Changed
1. `footnote_manager.py` - Core logic, data structures, scoring, candidate generation
2. `main_gui.py` - Enhanced GUI to display and handle candidate selections

## Usage
1. Load a DOCX file with footnotes
2. Open the footnote editor
3. For each footnote, the system will:
   - Auto-fill the best match in the reference field
   - Show a "후보 보기" (View Candidates) button
   - Click the button to expand and see top 3 candidates
   - Click any candidate to select it
4. Continue with bibliography generation and export as usual

## Benefits
- **Improved Accuracy**: Users can select from multiple reasonable options
- **Better User Experience**: Transparent matching process with visible alternatives
- **Academic Rigor**: Users maintain control over final citation format
- **Reduced Errors**: Less reliance on potentially incorrect automatic matching
- **Flexibility**: Easy to extend with additional candidate generation strategies

## Technical Details
See `IMPLEMENTATION_VERIFICATION.md` for detailed implementation verification against the original plan.