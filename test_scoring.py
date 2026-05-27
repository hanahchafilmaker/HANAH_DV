import sys
sys.path.insert(0, r'c:\Users\botto\Desktop\논문_교정기')

from footnote_manager import _calculate_similarity_score

# Test case 1: Perfect match in title, author, year (no DOI/ISBN)
parsed_ref1 = {
    "title": "Test Title",
    "author": "Test Author",
    "year": "2020",
    "doi": "",
    "isbn": ""
}
candidate_ref1 = "Test Author. Test Title. 2020."
print("Test 1 - Perfect match (no DOI/ISBN):")
print("  Source='crossref':", _calculate_similarity_score(parsed_ref1, candidate_ref1, "crossref"))
print("  Source='memory':", _calculate_similarity_score(parsed_ref1, candidate_ref1, "memory"))
print()

# Test case 2: Perfect match with DOI
parsed_ref2 = {
    "title": "Test Title",
    "author": "Test Author",
    "year": "2020",
    "doi": "10.1234/test",
    "isbn": ""
}
candidate_ref2 = "Test Author. Test Title. 2020. doi:10.1234/test"
print("Test 2 - Perfect match with DOI:")
print("  Source='crossref':", _calculate_similarity_score(parsed_ref2, candidate_ref2, "crossref"))
print("  Source='memory':", _calculate_similarity_score(parsed_ref2, candidate_ref2, "memory"))
print()

# Test case 3: Perfect match with ISBN
parsed_ref3 = {
    "title": "Test Title",
    "author": "Test Author",
    "year": "2020",
    "doi": "",
    "isbn": "978-3-16-148410-0"
}
candidate_ref3 = "Test Author. Test Title. 2020. ISBN 9783161484100"
print("Test 3 - Perfect match with ISBN:")
print("  Source='crossref':", _calculate_similarity_score(parsed_ref3, candidate_ref3, "crossref"))
print("  Source='memory':", _calculate_similarity_score(parsed_ref3, candidate_ref3, "memory"))
print()

# Test case 4: Half match in title and author, full year
parsed_ref4 = {
    "title": "Test Title",
    "author": "Test Author",
    "year": "2020",
    "doi": "",
    "isbn": ""
}
candidate_ref4 = "Tes Auth. Test Title. 2020."  # Similar but not exact
print("Test 4 - Partial match (title/author ~0.5, year exact):")
print("  Source='crossref':", _calculate_similarity_score(parsed_ref4, candidate_ref4, "crossref"))
print("  Source='memory':", _calculate_similarity_score(parsed_ref4, candidate_ref4, "memory"))
print()

# Test case 5: Partial match with DOI bonus
parsed_ref5 = {
    "title": "Test Title",
    "author": "Test Author",
    "year": "2020",
    "doi": "10.1234/test",
    "isbn": ""
}
candidate_ref5 = "Tes Auth. Test Title. 2020. doi:10.1234/test"
print("Test 5 - Partial match with DOI:")
print("  Source='crossref':", _calculate_similarity_score(parsed_ref5, candidate_ref5, "crossref"))
print("  Source='memory':", _calculate_similarity_score(parsed_ref5, candidate_ref5, "memory"))
print()

# Test case 6: Partial match with ISBN bonus
parsed_ref6 = {
    "title": "Test Title",
    "author": "Test Author",
    "year": "2020",
    "doi": "",
    "isbn": "978-3-16-148410-0"
}
candidate_ref6 = "Tes Auth. Test Title. 2020. ISBN 9783161484100"
print("Test 6 - Partial match with ISBN:")
print("  Source='crossref':", _calculate_similarity_score(parsed_ref6, candidate_ref6, "crossref"))
print("  Source='memory':", _calculate_similarity_score(parsed_ref6, candidate_ref6, "memory"))
print()