import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

def recommend_blogs(current_blog, top_n=3):
    from .models import Blog

    blogs = Blog.objects.exclude(id=current_blog.id)
    if not blogs.exists():
        return []

    blog_texts, blog_ids = [], []

    for blog in blogs:
        blocks = " ".join([block.content for block in blog.blocks.all() if block.content])
        raw_text = f"{blog.title} {blocks}"
        text = preprocess_text(raw_text)
        blog_texts.append(text)
        blog_ids.append(blog.id)

    current_blocks = " ".join([block.content for block in current_blog.blocks.all() if block.content])
    current_raw_text = f"{current_blog.title} {current_blocks}"
    current_text = preprocess_text(current_raw_text)

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([current_text] + blog_texts)

    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    top_indices = cosine_sim.argsort()[::-1][:10]
    top_blogs = [(blog_ids[i], cosine_sim[i]) for i in top_indices]

    current_topics = set(current_blog.topics or [])
    recommended = []
    for blog_id, sim_score in top_blogs:
        blog = Blog.objects.get(id=blog_id)
        blog_topics = set(blog.topics or [])
        if current_topics & blog_topics:
            recommended.append((blog, sim_score))

    recommended = sorted(recommended, key=lambda x: x[1], reverse=True)
    return [blog for blog, _ in recommended[:top_n]]


