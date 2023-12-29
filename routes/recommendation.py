from flask import Blueprint, jsonify, session, redirect
import requests
import time
import pandas as pd
from config import API_BASE_URL, CLIENT_ID, CLIENT_SECRET
from routes.recommendation_model import recommend_song_for_user

recommendation_routes = Blueprint('recommendation_routes', __name__)

PLAYLIST_ID = "3R3GqufjQSVlMPjCOIowDQ"

@recommendation_routes.route("/get-recommendation")
def get_recommendation():
    if "access_token" not in session or time.time() > session["expires_at"]:
        return redirect("/login")

    headers = {
        "Authorization": f"Bearer {session['access_token']}"
    }

    # Get user's top tracks
    top_tracks_url = API_BASE_URL + "/me/top/tracks"
    top_tracks_response = requests.get(top_tracks_url, headers=headers, params={"limit": 10})

    if top_tracks_response.status_code == 200:
        top_tracks_data = top_tracks_response.json()

        # Process and use the data as needed
        user_top_tracks = top_tracks_data["items"]

        # Get audio features and song information for user's top tracks
        user_top_tracks_data = []
        for track in user_top_tracks:
            track_id = track["id"]
            audio_features_url = API_BASE_URL + f"/audio-features/{track_id}"
            audio_features_response = requests.get(audio_features_url, headers=headers)

            if audio_features_response.status_code == 200:
                audio_features_data = audio_features_response.json()
                track_info = {
                    "track": {
                        "id": track_id,
                        "name": track["name"],
                        "artists": [{"name": artist["name"]} for artist in track["artists"]],
                        "audio_features": audio_features_data
                    }
                }
                user_top_tracks_data.append(track_info)
            else:
                return jsonify({"error": "Error in fetching audio features for top tracks"})


        # Create a DataFrame from the combined data
        user_top_tracks_df = pd.DataFrame(user_top_tracks_data)

        print("User Top Tracks DataFrame:")
        print(user_top_tracks_df)

        # Fetch playlist data
        playlist_tracks_url = API_BASE_URL + f"/playlists/{PLAYLIST_ID}/tracks"
        playlist_tracks_response = requests.get(playlist_tracks_url, headers=headers)

        if playlist_tracks_response.status_code == 200:
            playlist_tracks_data = playlist_tracks_response.json()["items"]

            # Get audio features for each track in the playlist
            playlist_tracks_info = []
            for item in playlist_tracks_data:
                track_id = item.get('track', {}).get('id')
                if track_id:
                    audio_features_url = API_BASE_URL + f"/audio-features/{track_id}"
                    audio_features_response = requests.get(audio_features_url, headers=headers)

                    if audio_features_response.status_code == 200:
                        audio_features_data = audio_features_response.json()
                        track_info = {
                            "track": {
                                "id": track_id,
                                "name": item['track']['name'],
                                "artists": [{"name": artist['name']} for artist in item['track']['artists']],
                                "audio_features": audio_features_data
                            }
                        }
                        playlist_tracks_info.append(track_info)
                    else:
                        return jsonify({"error": "Error in fetching audio features for playlist tracks"})


            # Create a DataFrame from the extracted information
            playlist_df = pd.DataFrame(playlist_tracks_info)

            print("Playlist DataFrame:")
            print(playlist_df)

            recommended_song_response = recommend_song_for_user(user_top_tracks_df, playlist_df)

            return recommended_song_response

        else:
            return jsonify({"error": "Error in fetching playlist tracks"})


    else:
        return jsonify({"error": "Error in fetching user's top tracks"})
