#!/usr/bin/env python
# Test script to verify improvements to the citation matching system

import json
import pickle
import copy
from footnote_manager import MatchCandidate, MatchResult, reset_citation_memory, citation_memory

def test_serialization():
    """Test that MatchResult and MatchCandidate can be serialized"""
    print("Testing serialization...")

    # Create test objects
    candidate1 = MatchCandidate(
        candidate_id="test1",
        matched_ref="Test Author, Test Title, 2023",
        confidence=0.85,
        source="memory",
        citation_type="FULL",
        doi="10.1234/test",
        preview="Test Author, Test Title..."
    )

    candidate2 = MatchCandidate(
        candidate_id="test2",
        matched_ref="Test Author, Test Title, 2023 (Crossref)",
        confidence=0.90,
        source="crossref",
        citation_type="FULL",
        doi="10.1234/test",
        preview="Test Author, Test Title..."
    )

    result = MatchResult(
        best_match=candidate1,
        candidates=[candidate1, candidate2],
        requires_user_selection=False
    )

    # Test to_dict method
    result_dict = result.to_dict()
    print(f"MatchResult to_dict: {result_dict}")

    # Test JSON serialization
    try:
        json_str = json.dumps(result_dict)
        print(f"JSON serialization successful: {json_str[:100]}...")
        # Test deserialization
        parsed_back = json.loads(json_str)
        print("JSON deserialization successful")
    except Exception as e:
        print(f"JSON serialization failed: {e}")
        return False

    # Test pickle serialization
    try:
        pickled = pickle.dumps(result)
        unpickled = pickle.loads(pickled)
        print("Pickle serialization successful")
    except Exception as e:
        print(f"Pickle serialization failed: {e}")
        return False

    # Test deepcopy
    try:
        copied = copy.deepcopy(result)
        print("Deepcopy successful")
    except Exception as e:
        print(f"Deepcopy failed: {e}")
        return False

    return True

def test_deduplication():
    """Test candidate deduplication"""
    print("\nTesting deduplication...")

    # Reset citation memory
    reset_citation_memory()

    # Create test candidates that should be deduplicated
    candidate1 = MatchCandidate(
        candidate_id="test1",
        matched_ref="Smith, John. AI Ethics in Modern Society. Press University, 2023.",
        confidence=0.85,
        source="memory",
        citation_type="FULL",
        preview="Smith, John. AI Ethics in Modern Society..."
    )

    candidate2 = MatchCandidate(
        candidate_id="test2",
        matched_ref="Smith, John. AI Ethics in Modern Society. Press University, 2023. doi:10.1234/test",
        confidence=0.90,
        source="crossref",
        citation_type="FULL",
        doi="10.1234/test",
        preview="Smith, John. AI Ethics in Modern Society..."
    )

    candidate3 = MatchCandidate(
        candidate_id="test3",
        matched_ref="Different Author. Different Title. Different Press, 2022.",
        confidence=0.75,
        source="memory",
        citation_type="FULL",
        preview="Different Author. Different Title..."
    )

    candidates = [candidate1, candidate2, candidate3]

    # Import the deduplication function
    from footnote_manager import _deduplicate_candidates
    unique_candidates = _deduplicate_candidates(candidates)

    print(f"Original candidates: {len(candidates)}")
    print(f"After deduplication: {len(unique_candidates)}")

    # Should have 2 unique candidates (candidate1 and candidate2 are duplicates)
    if len(unique_candidates) == 2:
        print("Deduplication working correctly")
        return True
    else:
        print("Deduplication not working as expected")
        return False

def test_confidence_scoring():
    """Test the confidence scoring system"""
    print("\nTesting confidence scoring...")

    from footnote_manager import _calculate_similarity_score, clean_reference

    # Test case: exact match should score high
    parsed_ref = {
        "title": "artificial intelligence ethics",
        "author": "john smith",
        "year": "2023"
    }

    candidate_ref = "John Smith. Artificial Intelligence Ethics. Press University, 2023."

    score = _calculate_similarity_score(parsed_ref, candidate_ref, "memory")
    print(f"Similarity score for good match: {score:.2f}")

    # Test case: poor match should score low
    poor_candidate_ref = "Jane Doe. Machine Learning Basics. Tech Press, 2020."
    poor_score = _calculate_similarity_score(parsed_ref, poor_candidate_ref, "memory")
    print(f"Similarity score for poor match: {poor_score:.2f}")

    # Good match should score higher than poor match
    if score > poor_score:
        print("Confidence scoring working correctly")
        return True
    else:
        print("Confidence scoring not working as expected")
        return False

if __name__ == "__main__":
    print("Running improvements test...\n")

    success = True
    success &= test_serialization()
    success &= test_deduplication()
    success &= test_confidence_scoring()

    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        exit(1)