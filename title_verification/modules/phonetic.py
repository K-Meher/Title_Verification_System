def soundex(word):
    """
    Generates Soundex code for a word
    """
    if not word:
        return ""

    word = word.lower()

    soundex_mapping = {
        'b': '1', 'f': '1', 'p': '1', 'v': '1',
        'c': '2', 'g': '2', 'j': '2', 'k': '2',
        'q': '2', 's': '2', 'x': '2', 'z': '2',
        'd': '3', 't': '3',
        'l': '4',
        'm': '5', 'n': '5',
        'r': '6'
    }

    # First letter kept as is
    first_letter = word[0].upper()

    encoded = []
    for char in word[1:]:
        encoded.append(soundex_mapping.get(char, '0'))

    # Remove consecutive duplicates
    filtered = []
    for i in range(len(encoded)):
        if i == 0 or encoded[i] != encoded[i - 1]:
            filtered.append(encoded[i])

    # Remove zeros
    filtered = [c for c in filtered if c != '0']

    # Build final soundex code
    soundex_code = first_letter + ''.join(filtered)
    soundex_code = soundex_code[:4].ljust(4, '0')

    return soundex_code


def phonetic_similarity(title1, title2):
    """
    Checks phonetic similarity word by word
    """
    words1 = title1.split()
    words2 = title2.split()

    matches = 0
    total = max(len(words1), len(words2))

    for w1 in words1:
        for w2 in words2:
            if soundex(w1) == soundex(w2):
                matches += 1
                break

    if total == 0:
        return 0.0

    return round(matches / total, 3)


# Simple test
if __name__ == "__main__":
    test_pairs = [
        ("pratap herald", "partap herold"),
        ("public awaz", "public aawaz"),
        ("qalam news", "kalam news"),
        ("daily reporter", "evening post")
    ]

    for t1, t2 in test_pairs:
        print(f"{t1}  <->  {t2}")
        print("Phonetic Similarity:", phonetic_similarity(t1, t2))
        print("-" * 40)
