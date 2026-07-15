COMMON_PREFIXES = [
    "india", "bharat", "national", "official"
]

COMMON_SUFFIXES = [
    "plus", "express", "news", "live", "24"
]


def remove_prefix_suffix(title):
    """
    Removes common prefixes and suffixes from title
    """
    words = title.split()

    # Remove prefix
    if words and words[0] in COMMON_PREFIXES:
        words = words[1:]

    # Remove suffix
    if words and words[-1] in COMMON_SUFFIXES:
        words = words[:-1]

    return " ".join(words)


def prefix_suffix_similarity(base_title, existing_title):
    """
    Checks if titles are same after removing prefix/suffix
    """
    cleaned_existing = remove_prefix_suffix(existing_title)
    cleaned_new = remove_prefix_suffix(base_title)

    return cleaned_existing == cleaned_new


# Simple test
if __name__ == "__main__":
    test_pairs = [
        ("india pratap herald", "pratap herald"),
        ("pratap herald plus", "pratap herald"),
        ("national public awaz", "public awaz"),
        ("daily reporter", "evening post")
    ]

    for t1, t2 in test_pairs:
        print(f"{t1}  <->  {t2}")
        print("Prefix/Suffix Match:", prefix_suffix_similarity(t1, t2))
        print("-" * 40)
