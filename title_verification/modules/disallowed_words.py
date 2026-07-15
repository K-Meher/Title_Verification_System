import re

def load_disallowed_words(file_path="data/disallowed_words.txt"):
    """
    Loads disallowed words from a text file
    """
    with open(file_path, "r") as file:
        words = [line.strip().lower() for line in file if line.strip()]
    return words


def check_disallowed_words(title, disallowed_words):
    """
    Checks if the title contains any disallowed words
    """
    violations = []

    for word in disallowed_words:
        # word boundary match to avoid partial false matches
        if re.search(rf"\b{re.escape(word)}\b", title):
            violations.append(word)

    return violations


# Simple test
if __name__ == "__main__":
    disallowed = load_disallowed_words()

    test_titles = [
        "Official Government News",
        "Public Awaz",
        "National Emblem Report",
        "Daily Fraud Alert"
    ]

    for t in test_titles:
        result = check_disallowed_words(t.lower(), disallowed)
        print(f"Title: {t}")
        if result:
            print("❌ Disallowed words found:", result)
        else:
            print("✅ No disallowed words")
        print("-" * 40)
