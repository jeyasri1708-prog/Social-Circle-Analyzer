# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.neighbors import kneighbors_graph
from sklearn.preprocessing import StandardScaler
import random
import uuid
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_mock_data(n_users=200):
    np.random.seed(42)
    random.seed(42)
    
    # Generate 4 distinct persona groups
    # 1. Active Techies
    # 2. Sports Fans (casual)
    # 3. Influencers (high followers, high posts)
    # 4. Lurkers (low posts, low followers, high likes)
    
    users = []
    
    for i in range(n_users):
        persona = random.choice(['Techie', 'Sports Fan', 'Influencer', 'Lurker'])
        
        if persona == 'Techie':
            posts = np.random.normal(5, 2)
            likes = np.random.normal(20, 5)
            followers = np.random.normal(300, 100)
            tech = 1
            sports = 0
            fashion = random.choice([0, 1])
        elif persona == 'Sports Fan':
            posts = np.random.normal(2, 1)
            likes = np.random.normal(10, 3)
            followers = np.random.normal(150, 50)
            tech = 0
            sports = 1
            fashion = random.choice([0, 1])
        elif persona == 'Influencer':
            posts = np.random.normal(10, 3)
            likes = np.random.normal(50, 15)
            followers = np.random.normal(5000, 1000)
            tech = random.choice([0, 1])
            sports = random.choice([0, 1])
            fashion = 1
        else: # Lurker
            posts = np.random.normal(0.5, 0.5)
            likes = np.random.normal(40, 10)
            followers = np.random.normal(50, 20)
            tech = random.choice([0, 1])
            sports = random.choice([0, 1])
            fashion = random.choice([0, 1])
            
        users.append({
            "id": str(uuid.uuid4())[:8],
            "name": f"User_{i+1}",
            "persona": persona,
            "posts_per_day": max(0, posts),
            "likes_given": max(0, likes),
            "followers": max(0, followers),
            "interest_tech": tech,
            "interest_sports": sports,
            "interest_fashion": fashion
        })
        
    return pd.DataFrame(users)

@app.get("/api/network")
def get_network_data(clusters: int = 4, n_users: int = 300):
    df = generate_mock_data(n_users)
    
    # Features for clustering
    features = ['posts_per_day', 'likes_given', 'followers', 'interest_tech', 'interest_sports', 'interest_fashion']
    X = df[features]
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # K-Means Clustering
    n_clusters = clusters
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(X_scaled)
    df['cluster'] = cluster_labels
    
    # Generate Graph using K-Nearest Neighbors
    # Create edges between similar nodes
    A = kneighbors_graph(X_scaled, n_neighbors=5, mode='connectivity', include_self=False)
    
    nodes = []
    for _, row in df.iterrows():
        nodes.append({
            "id": row['id'],
            "name": row['name'],
            "val": 10 + (row['followers'] / 500), # Node size based on followers
            "cluster": int(row['cluster']),
            "persona": row['persona'],
            "posts": float(row['posts_per_day']),
            "likes": float(row['likes_given']),
            "followers": float(row['followers'])
        })
        
    links = []
    # A is a sparse matrix
    rows, cols = A.nonzero()
    for u, v in zip(rows, cols):
        links.append({
            "source": df.iloc[u]['id'],
            "target": df.iloc[v]['id']
        })
        
    return {
        "nodes": nodes,
        "links": links
    }

# Mount static files
app.mount("/static", StaticFiles(directory="../static"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("../static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
