from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def tfidf_cosine_similarity(new_title, existing_titles):

    if not existing_titles:
        return 0.0

    documents = [new_title] + existing_titles

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    if tfidf_matrix.shape[0] < 2:
        return 0.0

    cosine_similarities = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    ).flatten()

    if len(cosine_similarities) == 0:
        return 0.0

    return max(cosine_similarities)