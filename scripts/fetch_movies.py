import json
import os
import requests
import time
import pandas as pd
from dotenv import load_dotenv
import tqdm


load_dotenv()
TOKEN = os.getenv("TMDB_TOKEN")
assert TOKEN, "TMDB_TOKEN environment variable is not set. Please set it in your .env file."
BASE_URL = "https://api.themoviedb.org/3"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "accept": "application/json"
}

START_YEAR = 1980
END_YEAR = 2025
PAGES_PER_YEAR = 12
OUTPUT_RAW = "data/raw_movies.jsonl"

os.makedirs("data", exist_ok=True)

def discover_ids(year):
    ids = []
    for page in range(1, PAGES_PER_YEAR + 1):
        r = requests.get(
            f"{BASE_URL}/discover/movie",
            headers=HEADERS,
            params={
                "primary_release_year": year,
                "sort_by": "revenue.desc",
                "vote_count.gte": 70,
                "page": page,
            },
        )
        if r.status_code != 200:
            print(f"  discover failed: {r.status_code}")
            break
        results = r.json().get("results", [])
        if not results:
            break
        ids.extend(m["id"] for m in results)
        time.sleep(0.25)
    return ids

def fetch_details(movie_id):
    try:
        r = requests.get(f"{BASE_URL}/movie/{movie_id}", headers=HEADERS)
    except requests.RequestException as e:
        print(f" {movie_id} details failed: {e}")
        return None
    if r.status_code != 200:
        print(f"  details failed: {r.status_code}")
        return None
    return r.json()

with open(OUTPUT_RAW, "w", encoding="utf-8") as f:
    for year in range(START_YEAR, END_YEAR + 1):
        ids = discover_ids(year)
        print(f"Year {year}: {len(ids)} movies found.")
        for movie_id in tqdm.tqdm(ids, desc=f"{year}"):
            details = fetch_details(movie_id)
            if details:
                f.write(json.dumps(details) + "\n")
            time.sleep(0.25)