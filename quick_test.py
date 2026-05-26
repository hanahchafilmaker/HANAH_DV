#!/usr/bin/env python
# Quick test of the serialization

import sys
sys.path.append('.')

try:
    from footnote_manager import MatchCandidate, MatchResult
    import json

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
    print("✅ MatchResult.to_dict() works")

    # Test JSON serialization
    json_str = json.dumps(result_dict)
    print("✅ JSON serialization works")

    # Test that we can recover the data
    parsed = json.loads(json_str)
    assert parsed['best_match']['matched_ref'] == "Test Author, Test Title, 2023"
    print("✅ JSON deserialization works")

    print("\n🎉 All quick tests passed!")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)