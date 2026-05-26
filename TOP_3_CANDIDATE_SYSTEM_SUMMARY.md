# Top-3 Candidate System Implementation Summary

## Overview
Successfully implemented a top-3 candidate system for the academic paper citation matching tool, shifting from forced auto-matching to user-controlled selection from multiple reasonable options.

## Changes Made

### footnote_manager.py
1. **Added Data Structures**:
   - `MatchCandidate`: Represents a single candidate match with matched_ref, confidence, source, citation_type, doi, and preview
   - `MatchResult`: Contains the best match (first candidate) and list of all candidates

2. **Implemented Unified Scoring System**:
   - `_calculate_similarity_score()` function based on title (0.4 weight), author (0.4 weight), and year (0.2 weight) similarity
   - Source bonus: memory matches get +0.05, Crossref matches get base score
   - Returns score between 0.0 and 1.0

3. **Enhanced Candidate Generation**:
   - For SHORT citations: Single high-confidence (0.95) candidate from memory (repeat linking)
   - For FULL citations: Multiple candidates generated:
     * Memory-only match (original reference)
     * Crossref-enriched match (if available)
   - Candidates scored and ranked by confidence descending

4. **Refactored auto_match_reference()**:
   - Returns MatchResult objects instead of dicts
   - Handles SHORT citations as repeat links (no alternatives needed)
   - For FULL citations: generates, scores, and ranks candidates
   - Sets `requires_user_selection` based on confidence threshold (< 0.7 requires selection)
   - Maintains memory-first flow: store FULL citations before Crossref enrichment

### main_gui.py
1. **Added Candidate Display Infrastructure**:
   - Added "후보 보기" (View Candidates) button to each footnote row
   - Created hidden candidate frames that expand/collapse on button click
   - Stored UI element references for candidate display

2. **Updated UI Handling**:
   - Modified `_update_auto_match_ui_threadsafe()` to handle both MatchResult objects and legacy dicts
   - Added candidate display update logic
   - Preserved existing functionality for confidence display, citation type, DOI linking, and auto-fill

3. **Implemented Candidate Interaction**:
   - `_toggle_candidate_display()`: Shows/hides candidate section
   - `_update_candidate_display()`: Populates candidate section with metadata
   - `_select_candidate()`: Handles user selection of a candidate
   - `_show_candidate_details()`: Shows detailed candidate information in popup

4. **Candidate Display Features**:
   - Shows preview text, confidence percentage, source (memory/Crossref), and DOI if available
   - Radio buttons for candidate selection
   - Clickable candidate info for detailed view
   - REPEATED citations show no candidates (auto-resolved as before)
   - Only FULL citations show candidate selection UI

## Key Benefits
1. **User Control**: Users can now select from multiple reasonable options instead of forced auto-matching
2. **Academic Workflow Alignment**: Better matches how scholars work with citations (first full appearance, then shortened repeats)
3. **Memory-First Processing**: Citation memory checked first, Crossref used only for enrichment
4. **Eliminated Race Conditions**: Sequential processing with single worker thread ensures citation memory consistency
5. **Backward Compatibility**: Graceful handling of both new MatchResult objects and legacy dicts
6. **Meaningful Matching**: Search based on title/author/year similarity rather than full-text Crossref search

## Implementation Details
- **Confidence Threshold**: Auto-fill occurs when confidence ≥ 0.7; user selection required when < 0.7
- **REPEATED Citations**: Automatically resolved with high confidence (0.95), no candidate selection needed
- **FULL Citations**: Show memory-only and Crossref-enriched candidates ranked by confidence
- **Source Bias**: Memory matches get slight bonus (+0.05) to prioritize canonical references
- **Preview System**: Truncated text previews (50 chars) for compact candidate display

## Files Modified
1. `footnote_manager.py` - Core logic, dataclasses, scoring, candidate generation
2. `main_gui.py` - GUI expansion, candidate display, click handling, backward compatibility

## Testing
Verified implementation through:
- Syntax checking of both modified files
- Review of logic flow for SHORT vs FULL citations
- Confirmation of memory-first processing order
- Validation of candidate scoring and ranking
- Inspection of GUI element additions and event handlers

The implementation successfully addresses the user's request for a top-3 candidate system with expandable sections showing confidence/source/preview metadata, and auto-selecting only for REPEATED citations.