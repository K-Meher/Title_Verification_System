import re

# Common periodicity terms as per PRGI practice
PERIODICITY_TERMS = [
    "daily", "weekly", "monthly", "yearly",
    "evening", "morning", "night"
]

def normalize_title(title):
    """
    Converts title into a standard normalized format
    """

    # 1. Convert to lowercase
    title = title.lower()

    # 2. Remove punctuation and special characters
    title = re.sub(r"[^a-z0-9\s]", "", title)

    # 3. Remove extra spaces
    title = re.sub(r"\s+", " ", title).strip()

    # 4. Separate periodicity terms
    words = title.split()
    base_words = []
    periodicity_found = []

    for word in words:
        if word in PERIODICITY_TERMS:
            periodicity_found.append(word)
        else:
            base_words.append(word)

    base_title = " ".join(base_words)

    return {
        "original_title": title,
        "base_title": base_title,
        "periodicity_terms": periodicity_found
    }


# Simple test
if __name__ == "__main__":
    sample_titles = [
        "Pratap Herald Daily",
        "THE National-Herald!!",
        "Public   Awaz   Weekly",
        "Evening News 24"
    ]

    for t in sample_titles:
        print(normalize_title(t))