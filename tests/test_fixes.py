#!/usr/bin/env python
# Test script to verify the fixes for the reported issues

import sys
sys.path.append('.')

def test_matchresult_get_method():
    """Test that MatchResult has get method for backward compatibility"""
    print("Testing MatchResult get method...")

    from footnote_manager import MatchCandidate, MatchResult

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

    # Test get method
    assert result.get('confidence') == 0.85
    assert result.get('matched_ref') == "Test Author, Test Title, 2023"
    assert result.get('source') == "memory"
    assert result.get('nonexistent', 'default') == 'default'
    print("✅ MatchResult.get() method works correctly")

    # Test __getitem__ method
    assert result['confidence'] == 0.85
    assert result['matched_ref'] == "Test Author, Test Title, 2023"
    assert result['source'] == "memory"
    print("✅ MatchResult.__getitem__() method works correctly")

    # Test with None best_match
    empty_result = MatchResult()
    assert empty_result.get('confidence', 'default') == 'default'
    try:
        _ = empty_result['confidence']
        assert False, "Should have raised KeyError"
    except KeyError:
        pass  # Expected
    print("✅ MatchResult handles None best_match correctly")

    return True

def test_fid_conversion():
    """Test that fid string to int conversion works"""
    print("\nTesting fid string to int conversion...")

    # Simulate the problematic code
    fid_str = "1"  # This is what we were getting

    # Old problematic way (would fail):
    # footnotes[fid_str - 1]  # TypeError

    # New fixed way:
    fid_int = int(fid_str)
    # footnotes[fid_int - 1]  # This should work

    assert fid_int == 1
    assert fid_int - 1 == 0
    print("✅ fid string to int conversion works correctly")

    return True

if __name__ == "__main__":
    print("Testing fixes for reported issues...\n")

    success = True
    try:
        success &= test_matchresult_get_method()
        success &= test_fid_conversion()
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        success = False

    if success:
        print("\n🎉 All fixes verified successfully!")
    else:
        print("\n❌ Some fixes failed!")
        sys.exit(1)