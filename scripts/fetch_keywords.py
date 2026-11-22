import os
import json
import requests
import time
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TMDB_TOKEN")
BASE = "https://api.themoviedb.org/3"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "accept": "application/json"
}

df = pd.read_csv("data\movies_clean.csv")
movie_ids = df["id"].tolist()

keyword_data = {}
print(f"Fetching keywords for {len(movie_ids)} movies...")

for i, movie_id in enumerate(movie_ids):
    r = requests.get(f"{BASE}/movie/{movie_id}/keywords", headers=HEADERS)
    if r.status_code == 200:
        keyword_data[movie_id] = r.json().get("keywords", [])
    else:
        keyword_data[movie_id] = []


    if (i + 1) % 100 == 0:
        print(f"Fetched keywords for {i + 1} movies.")

    time.sleep(0.25) 

with open("data/movie_keywords.json", "w", encoding="utf-8") as f:
    json.dump(keyword_data, f)

print("Keyword fetching complete. Data saved to data/movie_keywords.json.")