import sys
sys.path.insert(0, r'c:\Users\botto\Desktop\논문_교정기')

from footnote_manager import auto_match_reference, MatchResult, MatchCandidate, store_reference, reset_citation_memory, is_repeat_citation, get_stored_reference

print("Testing the updated implementation...")

# Reset citation memory for clean test
reset_citation_memory()

# Test case 1: Full citation - should generate a candidate from parsed data
print("\n1. Testing full citation:")
full_text = "John Doe. Test Book Title. Publisher, 2023."
result = auto_match_reference(full_text, "fn1")

if result and isinstance(result, MatchResult):
    print(f"   Best match: {result.best_match.matched_ref}")
    print(f"   Confidence: {result.best_match.confidence:.2f}")
    print(f"   Source: {result.best_match.source}")
    print(f"   Citation type: {result.best_match.citation_type}")
    print(f"   Number of candidates: {len(result.candidates)}")
    for i, candidate in enumerate(result.candidates):
        print(f"     Candidate {i+1}: {candidate.matched_ref} (confidence: {candidate.confidence:.2f})")
else:
    print(f"   Result: {result}")

# Store this reference for repeat detection
if result:
    # Extract short citation for storage
    short_cite = "John Doe, 2023"
    store_reference(short_cite, result.best_match.matched_ref, "fn1")
    print(f"\n   Stored reference for: {short_cite}")

# Test case 2: Same short citation - should detect as repeat
print("\n2. Testing short citation (repeat detection):")
short_text = "John Doe, 2023"
result2 = auto_match_reference(short_text, "fn1")

if result2 and isinstance(result2, MatchResult):
    print(f"   Best match: {result2.best_match.matched_ref}")
    print(f"   Confidence: {result2.best_match.confidence:.2f}")
    print(f"   Source: {result2.best_match.source}")
    print(f"   Citation type: {result2.best_match.citation_type}")
    print(f"   Number of candidates: {len(result2.candidates)}")
else:
    print(f"   Result: {result2}")

# Test case 3: Different full citation
print("\n3. Testing another full citation:")
full_text2 = "Jane Smith. Another Article. Journal of Studies, 2022."
result3 = auto_match_reference(full_text2, "fn2")

if result3 and isinstance(result3, MatchResult):
    print(f"   Best match: {result3.best_match.matched_ref}")
    print(f"   Confidence: {result3.best_match.confidence:.2f}")
    print(f"   Source: {result3.best_match.source}")
    print(f"   Citation type: {result3.best_match.citation_type}")
    print(f"   Number of candidates: {len(result3.candidates)}")
else:
    print(f"   Result: {result3}")

print("\nTest completed.")