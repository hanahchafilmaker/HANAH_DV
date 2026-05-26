#!/usr/bin/env python
# Simple verification script for serialization

import sys
sys.path.append('.')
from footnote_manager import MatchCandidate, MatchResult

def test_basic_serialization():
    print("Testing basic serialization...")

    # Create test objects
    candidate = MatchCandidate(
        candidate_id="test1",
        matched_ref="Test Author, Test Title, 2023",
        confidence=0.85,
        source="memory",
        citation_type="FULL",
        doi="10.1234/test",
        preview="Test Author, Test Title..."
    )

    result = MatchResult(
        best_match=candidate,
        candidates=[candidate],
        requires_user_selection=False
    )

    # Test to_dict
    result_dict = result.to_dict()
    print(f"MatchResult to_dict: {result_dict}")

    # Test that we can access the data
    assert result_dict['best_match']['matched_ref'] == "Test Author, Test Title, 2023"
    assert result_dict['requires_user_selection'] == False
    print("✅ Basic serialization test passed")

    return True

if __name__ == "__main__":
    try:
        test_basic_serialization()
        print("\n🎉 All serialization tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)