import json

with open("data/keywords/movie_keywords.json", "r") as f:
    data = json.load(f)
    all_based_on = []

    for k, v in data.items():
        if "based on" in str(v):
            index = [i for i, keyword in enumerate(v) if "based on" in str(keyword)]
            all_based_on.append(v[index[0]])

all_based_on = list(set(all_based_on))  # Remove duplicates

print(f"Found {len(all_based_on)} movies with 'based on' keywords.")
save_path = "data/keywords/based_on_keywords.json"
with open(save_path, "w") as f:
    json.dump(all_based_on, f, indent=4)

