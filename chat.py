import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os
from config import Config 

# --- Configuration Setup ---
MODEL_NAME = Config.MODEL_NAME
# This path should point to 'real_news_dataset.csv' if you updated config.py
NEWS_DATA_FILE = Config.NEWS_DATA_FILE 
EMBEDDING_FILE = Config.EMBEDDING_FILE

# --- BATCH CONFIGURATION ---
# Set the batch size. 10,000 is a safe balance between speed and RAM usage.
BATCH_SIZE = 10000 

def generate_embeddings_in_batches(model, texts, batch_size):
    """Encodes text data in smaller batches and concatenates the results."""
    total_records = len(texts)
    all_embeddings = []
    
    print(f"Total records to process: {total_records}")
    print(f"Processing in batches of: {batch_size}")

    for i in range(0, total_records, batch_size):
        batch_texts = texts[i:i + batch_size]
        
        # Calculate progress
        start_index = i
        end_index = i + len(batch_texts)
        total_batches = int(np.ceil(total_records / batch_size))
        
        print(f"-> Processing batch {i // batch_size + 1} / {total_batches} (Records {start_index} to {end_index})")
        
        # Use model.encode for generating embeddings
        batch_embeddings = model.encode(
            batch_texts, 
            show_progress_bar=False, 
            convert_to_numpy=True
        )
        all_embeddings.append(batch_embeddings)

    # Combine all batch embeddings into a single NumPy array
    return np.concatenate(all_embeddings, axis=0)


if __name__ == '__main__':
    print(f"--- BERT Pre-computation Script ---")
    print(f"Loading data from: {NEWS_DATA_FILE}...")
    
    # 1. Load the News Data (Need title and content columns)
    try:
        # Load only the necessary columns and use low_memory=False for large files
        news_df = pd.read_csv(NEWS_DATA_FILE, usecols=['title', 'content'], low_memory=False)
        
        # Critical: Drop rows where title or content is missing, as BERT needs text input
        news_df = news_df.dropna(subset=['title', 'content']) 
        
        if news_df.empty:
            raise ValueError("CSV file is empty after cleaning missing values.")
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Ensure the file exists, has 'title' and 'content' columns, and run with sufficient RAM.")
        exit()
        
    # 2. Combine title and content for embedding generation
    print(f"Using {len(news_df)} records after cleaning.")
    print("Combining 'title' and 'content' fields for richer embeddings...")
    
    # Concatenate title and content, separating them with a space
    texts_to_encode = (news_df['title'].astype(str) + " " + news_df['content'].astype(str)).tolist()
    
    # 3. Load Sentence-BERT Model
    print(f"Loading Sentence-BERT Model: {MODEL_NAME}...")
    try:
        model = SentenceTransformer(MODEL_NAME)
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please ensure sentence-transformers is installed.")
        exit()

    # 4. Generate Embeddings in Batches
    print("\nStarting batch embedding generation...")
    # 
    final_embeddings = generate_embeddings_in_batches(model, texts_to_encode, BATCH_SIZE)
    
    print(f"\nCompleted encoding. Final shape: {final_embeddings.shape}")
    
    # 5. Save Embeddings
    print(f"Saving embeddings to {EMBEDDING_FILE}...")
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(EMBEDDING_FILE), exist_ok=True)
        with open(EMBEDDING_FILE, 'wb') as f:
            pickle.dump(final_embeddings, f)
            
        print("Embeddings saved successfully!")
        print("--- Next Step: Run 'python app.py' ---")
        
    except Exception as e:
        print(f"Error saving embeddings: {e}")
        