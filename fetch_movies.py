import json
import os
import requests
import time
import pandas as pd
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("TMDB_TOKEN")
assert TOKEN, "TMDB_TOKEN environment variable is not set. Please set it in your .env file."
BASE_URL = "https://api.themoviedb.org/3"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "accept": "application/json"
}

START_YEAR = 1990
END_YEAR = 2026
OUTPUT_RAW = "data/raw_movies.jsonl"

os.makedirs("data", exist_ok=True)

def discover_ids(year):
    ids =  []
    page = 1
    total_pages = 1
    while page <= total_pages:
        r = requests.get(
            f'{BASE_URL}/discover/movie',
            headers=HEADERS,
            params={
                'primary_release_year': year,
                'vote_count.gte': 100,
                'include_adult': 'false',
                'sort_by': 'original_title.asc',
                'page': page
            }
        )
        if r.status_code != 200:
            print(f'  discover failed: {r.status_code} {r.text}')
            break

        data = r.json()
        if page == 1:
            total_pages = data.get('total_pages', 1)
            total_results = data.get('total_results', 0)
            print(f'  {year}: {total_results} movies across {total_pages} pages.')

        results = data.get('results', [])
        if not results:
            break
        ids.extend([movie['id'] for movie in results])
        time.sleep(0.25)  # To avoid hitting rate limits
    return ids