#!/usr/bin/env python
# Test the core logic of the footnote manager

import sys
sys.path.append('.')

def test_core_logic():
    print("Testing core logic of footnote_manager...")

    try:
        from footnote_manager import (
            MatchCandidate, MatchResult,
            reset_citation_memory, citation_memory,
            auto_match_reference, clean_reference,
            looks_like_full_citation, looks_like_short_citation,
            normalize_key, _calculate_similarity_score,
            _deduplicate_candidates, _normalize_for_dedup
        )

        print("✓ All imports successful")

        # Test 1: Basic data structures
        print("\n1. Testing data structures...")
        candidate = MatchCandidate(
            candidate_id="test1",
            matched_ref="John Doe. Test Book. Publisher, 2023.",
            confidence=0.85,
            source="memory",
            citation_type="FULL",
            doi="10.1234/test",
            preview="John Doe. Test Book..."
        )

        result = MatchResult(
            best_match=candidate,
            candidates=[candidate],
            requires_user_selection=False
        )

        # Test to_dict
        result_dict = result.to_dict()
        assert result_dict['best_match']['matched_ref'] == "John Doe. Test Book. Publisher, 2023."
        assert result_dict['requires_user_selection'] == False
        print("✓ MatchResult.to_dict() works")

        # Test get method
        assert result.get('confidence') == 0.85
        assert result.get('matched_ref') == "John Doe. Test Book. Publisher, 2023."
        assert result.get('nonexistent', 'default') == 'default'
        print("✓ MatchResult.get() works")

        # Test __getitem__ method
        assert result['confidence'] == 0.85
        assert result['matched_ref'] == "John Doe. Test Book. Publisher, 2023."
        print("✓ MatchResult.__getitem__() works")

        # Test 2: Memory management
        print("\n2. Testing memory management...")
        reset_citation_memory()
        assert len(citation_memory) == 0
        print("✓ Citation memory reset works")

        # Test 3: Citation classification
        print("\n3. Testing citation classification...")
        full_text = "John Doe. Artificial Intelligence Ethics. Tech Press, 2023."
        short_text = "John Doe. Artificial Intelligence Ethics, 23-25."

        assert looks_like_full_citation(full_text) == True
        assert looks_like_short_citation(short_text) == True
        assert looks_like_full_citation(short_text) == False  # Should not be both
        print("✓ Citation classification works")

        # Test 4: Normalization
        print("\n4. Testing normalization...")
        key1 = normalize_key("John Doe", "Test Book")
        key2 = normalize_key("  JOHN  DOE  ", "  TEST  BOOK  ")
        assert key1 == key2
        print("✓ Normalization works")

        # Test 5: Similarity scoring
        print("\n5. Testing similarity scoring...")
        parsed = clean_reference("John Doe. Artificial Intelligence Ethics. Tech Press, 2023.")
        score = _calculate_similarity_score(parsed, "John Doe. Artificial Intelligence Ethics. Tech Press, 2023.", "memory")
        assert score > 0.8  # Should be high for exact match
        print(f"✓ Similarity score: {score:.2f}")

        # Test 6: Deduplication
        print("\n6. Testing deduplication...")
        cand1 = MatchCandidate("id1", "Ref A", 0.8, "memory", "FULL", "", "Ref A...")
        cand2 = MatchCandidate("id2", "Ref A", 0.9, "crossref", "FULL", "", "Ref A...")  # Same ref
        cand3 = MatchCandidate("id3", "Ref B", 0.7, "memory", "FULL", "", "Ref B...")

        candidates = [cand1, cand2, cand3]
        unique = _deduplicate_candidates(candidates)
        assert len(unique) == 2  # Should remove duplicate Ref A
        print(f"✓ Deduplication: {len(candidates)} -> {len(unique)} candidates")

        # Test 7: Auto match reference (basic)
        print("\n7. Testing auto_match_reference...")
        # First, process a full citation to store in memory
        full_result = auto_match_reference("John Doe. Test Book. Publisher, 2023.", "fn1")
        assert full_result is not None
        assert full_result.best_match is not None
        assert len(citation_memory) == 1
        print("✓ First full citation stored in memory")

        # Then, process a short citation that should match
        short_result = auto_match_reference("John Doe. Test Book, 23-25.", "fn2")
        assert short_result is not None
        assert short_result.best_match is not None
        assert short_result.best_match.citation_type == "REPEATED"
        assert short_result.best_match.confidence == 0.95
        print("✓ Short citation correctly identified as repeat")

        print("\n🎉 All core logic tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_core_logic()
    if not success:
        sys.exit(1)