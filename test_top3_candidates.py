import sys
sys.path.insert(0, r'c:\Users\botto\Desktop\논문_교정기')

from footnote_manager import auto_match_reference, MatchResult, MatchCandidate

def test_auto_match_reference():
    print("Testing auto_match_reference function...")

    # Test case 1: Full citation
    print("\n1. Testing full citation:")
    full_text = "John Doe. Test Book Title. Publisher, 2023."
    result = auto_match_reference(full_text, "fn1")

    if result and isinstance(result, MatchResult):
        print(f"   Best match: {result.best_match.matched_ref}")
        print(f   Confidence: {result.best_match.confidence:.2f}")
        print(f"   Source: {result.best_match.source}")
        print(f"   Citation type: {result.best_match.citation_type}")
        print(f"   Number of candidates: {len(result.candidates)}")
        for i, candidate in enumerate(result.candidates):
            print(f"     Candidate {i+1}: {candidate.matched_ref} (confidence: {candidate.confidence:.2f})")
    else:
        print(f"   Result: {result}")

    # Test case 2: Short citation (should not match yet as no memory)
    print("\n2. Testing short citation (no prior memory):")
    short_text = "John Doe, 2023"
    result = auto_match_reference(short_text, "fn2")

    if result and isinstance(result, MatchResult):
        print(f"   Best match: {result.best_match.matched_ref}")
        print(f"   Confidence: {result.best_match.confidence:.2f}")
        print(f"   Source: {result.best_match.source}")
        print(f"   Citation type: {result.best_match.citation_type}")
        print(f"   Number of candidates: {len(result.candidates)}")
    else:
        print(f"   Result: {result}")

    # Test case 3: Another full citation
    print("\n3. Testing another full citation:")
    full_text2 = "Jane Smith. Another Article. Journal of Studies, 2022."
    result = auto_match_reference(full_text2, "fn3")

    if result and isinstance(result, MatchResult):
        print(f"   Best match: {result.best_match.matched_ref}")
        print(f"   Confidence: {result.best_match.confidence:.2f}")
        print(f"   Source: {result.best_match.source}")
        print(f"   Citation type: {result.best_match.citation_type}")
        print(f"   Number of candidates: {len(result.candidates)}")
    else:
        print(f"   Result: {result}")

if __name__ == "__main__":
    test_auto_match_reference()