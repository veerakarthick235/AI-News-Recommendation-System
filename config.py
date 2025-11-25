import os

# --- General Application Settings ---
class Config:
    # Set this to False when deploying to production
    DEBUG = True
    
    # Secret key for session management (SECURITY WARNING: CHANGE THIS FOR PRODUCTION!)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'this_is_a_development_secret_key_change_it_now')

    # --- Machine Learning Model & Data Paths ---
    
    # BERT model name for Sentence-Transformers
    MODEL_NAME = 'all-MiniLM-L6-v2'
    
    # 📰 Data File Paths (Relative to the app.py root)
    DATA_DIR = 'news_data'
    
    # PATH TO THE INTEGRATED DATASET
    NEWS_DATA_FILE = os.path.join(DATA_DIR, 'real_news_dataset.csv')
    
    # File where the pre-computed embeddings will be stored (created by precompute_embeddings.py)
    EMBEDDING_FILE = os.path.join(DATA_DIR, 'embeddings.pkl')

    # ⚙️ Recommendation Parameters
    # Number of top recommendations to return to the frontend
    TOP_K_RECOMMENDATIONS = 10 
    
    # --- Server Settings ---
    HOST = '127.0.0.1' # Loopback address for local development
    PORT = 5000