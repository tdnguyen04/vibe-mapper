import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import os
from dotenv import load_dotenv

load_dotenv()

def get_spotify_client():
    """Handles authentication and returns the client."""
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-library-read"
    ))

def parse_track(item):
    """Helper: Extracts only the data we care about from the raw Spotify response."""
    track = item['track']
    return {
        "id": track['id'],
        "name": track['name'],
        "artist": track['artists'][0]['name'],
        "album": track['album']['name'],
        "url": track['external_urls']['spotify'],
        "cover_image": track['album']['images'][0]['url'] if track['album']['images'] else None
    }

def extract_library():
    sp = get_spotify_client()
    print("✅ Connected to Spotify.")

    all_songs = []
    limit = 50
    offset = 0

    while True:
        # Fetch the batch
        results = sp.current_user_saved_tracks(limit=limit, offset=offset)
        items = results['items']
        
        if not items:
            break

        print(f"   📡 Fetching songs {offset} to {offset + len(items)}...")

        # Clean List Comprehension (Replaces the loop)
        batch_songs = [parse_track(item) for item in items]
        all_songs.extend(batch_songs)

        offset += limit

    return all_songs

if __name__ == "__main__":
    songs = extract_library()
    
    with open('my_raw_songs.json', 'w', encoding='utf-8') as f:
        json.dump(songs, f, indent=2, ensure_ascii=False)
    
    print(f"✨ Done! Saved {len(songs)} songs to 'my_raw_songs.json'.")