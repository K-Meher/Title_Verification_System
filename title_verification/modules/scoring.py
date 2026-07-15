def calculate_final_score(edit_score,
                          phonetic_score,
                          prefix_suffix_match,
                          combination_violation):
    """
    Aggregates all similarity checks into final probability score
    """

    # Policy violations override similarity
    if prefix_suffix_match:
        return 1.0, "Prefix/Suffix violation"

    if combination_violation:
        return 1.0, "Combination violation"

    # Otherwise take maximum similarity
    final_score = max(edit_score, phonetic_score)

    return round(final_score, 3), "Similarity based"


def classify_title(score):
    """
    Classifies title based on probability threshold
    """

    if score >= 0.9:
        return "Duplicate"
    elif score >= 0.75:
        return "Likely Duplicate"
    else:
        return "Acceptable"


# Simple test
if __name__ == "__main__":

    test_cases = [
        (0.92, 0.85, False, False),
        (0.60, 0.95, False, False),
        (0.40, 0.50, True, False),
        (0.50, 0.40, False, True),
        (0.60, 0.65, False, False)
    ]

    for edit, phonetic, prefix, combo in test_cases:
        score, reason = calculate_final_score(edit, phonetic, prefix, combo)
        classification = classify_title(score)

        print("Edit:", edit,
              "Phonetic:", phonetic,
              "Prefix:", prefix,
              "Combo:", combo)
        print("Final Score:", score)
        print("Reason:", reason)
        print("Classification:", classification)
        print("-" * 50)
