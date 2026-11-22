import os
import json
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TMDB_TOKEN")
BASE = "https://api.themoviedb.org/3"
HEADERS = {"accept": "application/json", "Authorization": f"Bearer {TOKEN}"}

# 1. Load the clean dataset
df = pd.read_csv("data/movies_clean.csv")
movie_ids = df["id"].tolist()

# 2. Try to load the existing JSON
try:
    with open("data/keywords/movie_keywords.jsonl", "r") as f:
        keywords_data = json.load(f)
    print(f"Successfully loaded existing JSON with {len(keywords_data)} movies.")
except json.JSONDecodeError:
    print("JSON file is corrupted/truncated. Starting fresh.")
    keywords_data = {}

# 3. Find which IDs are missing
missing_ids = [mid for mid in movie_ids if str(mid) not in keywords_data]
print(f"Need to fetch {len(missing_ids)} missing movies...")

# 4. Fetch the missing IDs
for i, mid in enumerate(missing_ids):
    r = requests.get(f"{BASE}/movie/{mid}/keywords", headers=HEADERS)
    if r.status_code == 200:
        keywords_data[str(mid)] = [k["name"] for k in r.json().get("keywords", [])]
    else:
        keywords_data[str(mid)] = []
        
    if (i + 1) % 200 == 0:
        print(f"  Fetched {i + 1} / {len(missing_ids)}")
    time.sleep(0.25)

# 5. Save it beautifully formatted (indent=4) and as a flat list of strings!
pretty_data = {}
for k, v in keywords_data.items():
    # Extract just the string names from the dicts
    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
        pretty_data[k] = [item["name"] for item in v]
    else:
        pretty_data[k] = v

with open("data/keywords/movie_keywords.json", "w") as f:
    json.dump(pretty_data, f, indent=4)

print("Done! File is fixed and formatted.")