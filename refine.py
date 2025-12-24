import json
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

# --- THE VIBE DICTIONARY ---
# We map tags to (Energy, Valence)
TAG_SCORES = {
    "pop": (0.8, 0.8), "dance": (0.9, 0.8), "happy": (0.8, 0.9), "disco": (0.85, 0.9),
    "metal": (0.95, 0.2), "rock": (0.8, 0.4), "punk": (0.9, 0.3), "trap": (0.85, 0.3),
    "chill": (0.3, 0.8), "jazz": (0.4, 0.7), "soul": (0.4, 0.8), "acoustic": (0.3, 0.7),
    "sad": (0.2, 0.2), "ambient": (0.2, 0.5), "indie": (0.6, 0.5), "lo-fi": (0.3, 0.6)
}

def get_lastfm_tags(artist, track):
    """
    GOAL: Ask Last.fm for tags.
    1. Get API Key from os.getenv
    2. Define the URL (http://ws.audioscrobbler.com/2.0/)
    3. Set up params (method='track.getTopTags', artist, track, api_key, format='json')
    4. Use requests.get()
    5. Return the list of tags (or an empty list if it fails)
    """
    api_key = os.getenv('LASTFM_API_KEY')
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        "method":"track.getTopTags",
        "track": track,
        "artist": artist,
        "api_key": api_key,
        "format": "json",
        "autocorrect": 1
    }
    print(params)
    res = requests.get(url, params=params,timeout=5)
    if not res.ok:
        return []
    data = res.json()

    if 'error' in data:
        print(data)
        return []

    toptags = data.get('toptags', {})
    tags_raw = toptags.get('tag', [])

    if isinstance(tags_raw, dict):
        tags_raw = [tags_raw]
    
    clean_tags = []
    for t in tags_raw:
        clean_tags.append(t['name'].lower())

    return clean_tags[:5]

def calculate_vibe(tags):
    """
    GOAL: Turn a list of strings ['pop', 'dance'] into numbers (0.8, 0.8).
    1. Loop through the input tags.
    2. Check if the tag exists in TAG_SCORES.
    3. If yes, add the energy/valence to a running total.
    4. Divide by the count to get the average.
    5. Return (energy, valence).
    """
    total_energy = 0
    total_valence = 0
    cnt = 0
    for tag in tags:
        for key, (e, v) in TAG_SCORES.items():
            if key in tag:
                total_energy += e
                total_valence += v
                cnt += 1
    
    if cnt == 0:
        return None
    
    avg_energy = round(total_energy / cnt, 2)
    avg_valence = round(total_valence / cnt, 2)

    return (avg_energy, avg_valence)
    

def refine_data():
    print("⚗️ Starting Refinery...")
    
    processed_songs = []
    fetched_songs = []
    # 1. Load 'my_raw_songs.json' (Don't forget encoding='utf-8'!)
    with open("my_raw_songs.json", "r", encoding="utf-8") as file:
        fetched_songs = json.load(file)
    
    print(fetched_songs[:5])
    print(calculate_vibe(get_lastfm_tags(artist=fetched_songs[0]["artist"], track=fetched_songs[0]["name"])))

    
    # 2. Loop through every song in the loaded data
    #    a. Call get_lastfm_tags()
    #    b. Call calculate_vibe()
    #    c. Add the new data to the song dictionary
    #    d. Append to processed_songs list
    for song in fetched_songs:
        tags = get_lastfm_tags(artist=song["artist"], track=song["name"])
        vibe = calculate_vibe(tags)
        if vibe == None:
            vibe = (0.5, 0.5)
        song["tags"] = {
            "energy": vibe[0],
            "valence": vibe[1]
        }
        processed_songs.append(song)
        

    # 3. Save the result to 'my_refined_songs.json'
    with open("my_refined_songs.json", "w", encoding="utf-8") as file:
        json.dump(processed_songs, file, indent=2)
    
    print("Done!")

if __name__ == "__main__":
    refine_data()
    # print(get_lastfm_tags(artist="radiohead", track="paranoid android"))
    # print(get_lastfm_tags(artist="Vũ.", track="Nếu Những Tiếc Nuối"))
    # print(get_lastfm_tags(artist="Nếu Những Tiếc Nuối", track="Vũ."))
    
    # # Test 2: Removed Dot
    # print(get_lastfm_tags(artist="Vũ", track="Nếu Những Tiếc Nuối"))

    # # Test 3: Removed Accents (English style)
    # print(get_lastfm_tags(artist="Vu", track="Neu Nhung Tiec Nuoi"))