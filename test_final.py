import sys
sys.path.insert(0, r'c:\Users\botto\Desktop\논문_교정기')

from footnote_manager import auto_match_reference, MatchResult, store_reference, reset_citation_memory

print("=" * 60)
print("FINAL TEST OF TOP-3 CANDIDATE SYSTEM")
print("=" * 60)

# Reset citation memory for clean test
reset_citation_memory()

# Test case 1: Full citation - should generate multiple candidates
print("\n1. Testing full citation generation (should show top-3 candidates):")
full_text = "John Doe. Test Book Title. Publisher, 2023."
result = auto_match_reference(full_text, "fn1")

if result and isinstance(result, MatchResult):
    print(f"   ✓ Best match: {result.best_match.matched_ref}")
    print(f"   ✓ Confidence: {result.best_match.confidence:.2f}")
    print(f"   ✓ Source: {result.best_match.source}")
    print(f"   ✓ Citation type: {result.best_match.citation_type}")
    print(f"   ✓ Number of candidates: {len(result.candidates)}")
    for i, candidate in enumerate(result.candidates):
        print(f"     Candidate {i+1}: {candidate.matched_ref}")
        print(f"       Confidence: {candidate.confidence:.2f}")
        print(f"       Source: {candidate.source}")
else:
    print(f"   ✗ Result: {result}")

# Store this reference for repeat detection
if result:
    # Extract short citation for storage
    short_cite = "John Doe, 2023"
    store_reference(short_cite, result.best_match.matched_ref, "fn1")
    print(f"\n   ✓ Stored reference for: {short_cite}")

# Test case 2: Same short citation - should detect as repeat with high confidence
print("\n2. Testing repeat citation detection:")
short_text = "John Doe, 2023"
result2 = auto_match_reference(short_text, "fn1")

if result2 and isinstance(result2, MatchResult):
    print(f"   ✓ Best match: {result2.best_match.matched_ref}")
    print(f"   ✓ Confidence: {result2.best_match.confidence:.2f}")
    print(f"   ✓ Source: {result2.best_match.source}")
    print(f"   ✓ Citation type: {result2.best_match.citation_type}")
    print(f"   ✓ Number of candidates: {len(result2.candidates)}")
    # Note: For repeat citations, candidates are generated but not displayed in UI per requirements
else:
    print(f"   ✗ Result: {result2}")

# Test case 3: Different full citation with multiple authors (to test et al. variation)
print("\n3. Testing full citation with multiple authors:")
full_text2 = "John Doe and Jane Smith. Another Article. Journal of Studies, 2022."
result3 = auto_match_reference(full_text2, "fn2")

if result3 and isinstance(result3, MatchResult):
    print(f"   ✓ Best match: {result3.best_match.matched_ref}")
    print(f"   ✓ Confidence: {result3.best_match.confidence:.2f}")
    print(f"   ✓ Source: {result3.best_match.source}")
    print(f"   ✓ Citation type: {result3.best_match.citation_type}")
    print(f"   ✓ Number of candidates: {len(result3.candidates)}")
    for i, candidate in enumerate(result3.candidates):
        print(f"     Candidate {i+1}: {candidate.matched_ref}")
        print(f"       Confidence: {candidate.confidence:.2f}")
        print(f"       Source: {candidate.source}")
else:
    print(f"   ✗ Result: {result3}")

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)