def levenshtein_distance(s1, s2):
    """
    Computes Levenshtein distance between two strings
    """
    if s1 == s2:
        return 0

    len_s1 = len(s1)
    len_s2 = len(s2)

    # Create distance matrix
    dp = [[0] * (len_s2 + 1) for _ in range(len_s1 + 1)]

    # Initialize base cases
    for i in range(len_s1 + 1):
        dp[i][0] = i
    for j in range(len_s2 + 1):
        dp[0][j] = j

    # Compute distances
    for i in range(1, len_s1 + 1):
        for j in range(1, len_s2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # deletion
                dp[i][j - 1] + 1,      # insertion
                dp[i - 1][j - 1] + cost  # substitution
            )

    return dp[len_s1][len_s2]


def similarity_score(s1, s2):
    """
    Converts edit distance into similarity score (0 to 1)
    """
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0

    distance = levenshtein_distance(s1, s2)
    similarity = 1 - (distance / max_len)
    return round(similarity, 3)


# Simple test
if __name__ == "__main__":
    test_pairs = [
        ("pratap", "partap"),
        ("national herald", "national herold"),
        ("public awaz", "public aawaz"),
        ("daily news", "evening post")
    ]

    for t1, t2 in test_pairs:
        print(f"{t1}  <->  {t2}")
        print("Edit Distance:", levenshtein_distance(t1, t2))
        print("Similarity Score:", similarity_score(t1, t2))
        print("-" * 40)
