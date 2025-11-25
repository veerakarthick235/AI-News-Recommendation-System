import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
from config import Config 

# --- FLASK APPLICATION SETUP ---
app = Flask(__name__)
app.config.from_object(Config)

# --- Configuration & Global Variables ---
MODEL_NAME = app.config['MODEL_NAME']
EMBEDDING_FILE = app.config['EMBEDDING_FILE']
NEWS_DATA_FILE = app.config['NEWS_DATA_FILE']
TOP_K = app.config['TOP_K_RECOMMENDATIONS']

model = None
article_embeddings = None
news_df = None


# --- SYSTEM INITIALIZATION (Executed once on startup) ---

def load_system_components():
    """Loads the BERT model, pre-computed embeddings, and the data file."""
    global model, article_embeddings, news_df
    
    try:
        print("Loading Sentence-BERT Model...")
        model = SentenceTransformer(MODEL_NAME)
        
        print("Loading Pre-computed Embeddings...")
        with open(EMBEDDING_FILE, 'rb') as f:
            article_embeddings = pickle.load(f)
            
        print("Loading Real News Dataset...")
        # Load all columns we need for display and linkage
        news_df = pd.read_csv(NEWS_DATA_FILE, low_memory=False)
        
        # Filter the DataFrame to only include rows that were successfully embedded 
        # (i.e., those without NaN in 'title' or 'content')
        news_df = news_df.dropna(subset=['title', 'content']).reset_index(drop=True)

        if len(article_embeddings) != len(news_df):
            # This is a critical check to ensure vectors align with data rows
            print(f"Mismatch: Embeddings ({len(article_embeddings)}) vs Data ({len(news_df)})")
            raise ValueError("Embeddings and Data Frame size mismatch. Re-run precompute_embeddings.py.")
        
        print(f"System loaded successfully. Ready to serve {len(news_df)} articles.")
        
    except FileNotFoundError as e:
        print(f"FATAL ERROR: Required file not found: {e.filename}")
        print("Please ensure you have run 'python precompute_embeddings.py' first.")
        exit()
    except Exception as e:
        print(f"FATAL ERROR during startup: {e}")
        exit()

# --- RECOMMENDATION CORE LOGIC ---

def get_recommendations(user_query, k=TOP_K):
    """
    Performs semantic search using Cosine Similarity on BERT embeddings.
    [Image of Cosine Similarity calculation in vector space]
    """
    if model is None or article_embeddings is None:
        return []

    # 1. Generate embedding for the user's query
    query_embedding = model.encode([user_query])
    
    # 2. Calculate cosine similarity against all stored embeddings
    similarities = cosine_similarity(query_embedding, article_embeddings)[0]
    
    # 3. Get the indices of the top K most similar articles
    top_indices = np.argsort(similarities)[::-1][:k]
    
    # 4. Retrieve the corresponding news records
    recommended_news = news_df.iloc[top_indices].copy()
    
    # 5. Add the similarity score
    scores = similarities[top_indices]
    recommended_news['similarity_score'] = scores
    
    # 6. Return as a list of dictionaries
    return recommended_news.to_dict('records')


# --- FLASK ROUTES ---

@app.route('/')
def home():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """Handles the user query and returns news recommendations."""
    data = request.json
    user_input = data.get('query')
    
    if not user_input:
        return jsonify({'error': 'No query provided. Please enter your news interests.'}), 400
        
    try:
        recommendations = get_recommendations(user_input)
        
        # Ensure similarity_score is a standard float for JSON serialization
        formatted_recommendations = []
        for rec in recommendations:
            rec['similarity_score'] = float(rec['similarity_score'])
            formatted_recommendations.append(rec)
            
        return jsonify(formatted_recommendations)
        
    except Exception as e:
        print(f"Recommendation processing error: {e}")
        return jsonify({'error': 'An internal server error occurred during semantic search.'}), 500


# --- APPLICATION RUNNER ---

if __name__ == '__main__':
    load_system_components()
    print(f"Starting Flask server on http://{Config.HOST}:{Config.PORT}/")
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)