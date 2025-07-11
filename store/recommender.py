import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from .models import Product
import nltk
from nltk.corpus import stopwords

# Pastikan stopwords sudah di-download jika ingin digunakan
# nltk.download('stopwords')

def get_recommendations(product, top_n=4):
    products = list(Product.objects.filter(available=True))
    if len(products) <= 1:
        return []
    product_ids = []
    corpus = []
    for p in products:
        product_ids.append(p.id)
        # Gabungkan deskripsi, kategori, dan harga sebagai fitur teks
        text = f"{p.name} {p.description} {p.category.name} {p.price}"
        corpus.append(text)
    # TF-IDF vectorization
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(corpus)
    # Cari index produk yang diminta
    try:
        idx = product_ids.index(product.id)
    except ValueError:
        return []
    # Hitung similarity
    cosine_sim = linear_kernel(tfidf_matrix[idx:idx+1], tfidf_matrix).flatten()
    # Urutkan berdasarkan skor similarity (kecuali diri sendiri)
    similar_indices = np.argsort(cosine_sim)[::-1]
    recommendations = []
    for i in similar_indices:
        if product_ids[i] != product.id:
            recommendations.append(products[int(i)])
        if len(recommendations) >= top_n:
            break
    return recommendations
