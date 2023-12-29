import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from flask import jsonify
import numpy as np

def recommend_song_for_user(user_top_tracks_df, playlist_df):
    # Assuming 'danceability', 'energy', 'tempo', 'valence' are relevant numerical features
    features = ['danceability', 'energy', 'tempo', 'valence', 'instrumentalness', 'key', 'loudness', 'speechiness']

    # Extract audio features from the 'track' column in user_top_tracks_df
    user_top_tracks_features = user_top_tracks_df['track'].apply(lambda x: [x.get('audio_features', {}).get(feature, '') for feature in features])

    # Extract audio features from the 'track' column in playlist_df
    playlist_features = playlist_df['track'].apply(lambda x: [x.get('audio_features', {}).get(feature, '') for feature in features])

    try:
        # Compute similarity scores between each user track and all playlist tracks
        similarity_matrix = cosine_similarity(user_top_tracks_features.tolist(), playlist_features.tolist())
    except Exception as e:
        print(f"Error in cosine_similarity: {str(e)}")
        return

    print("\nsimilarity_matrix:\n", similarity_matrix)

    if not similarity_matrix.any():
        print("Similarity matrix is empty")
        return

    # Find the indices of the maximum values in the similarity matrix
    max_similarity_indices = np.unravel_index(similarity_matrix.argmax(), similarity_matrix.shape)

    # Extract the corresponding row and column indices
    user_index, playlist_index = max_similarity_indices

    # Print some information for troubleshooting
    print("User index:", user_index)
    print("Playlist index:", playlist_index)

    # Directly access the 'name' field in the 'track' column
    recommended_song_name = playlist_df.iloc[playlist_index]['track'].get('name')

    if pd.isna(recommended_song_name):
        print("Recommended song name is NaN")
        return

    print("Recommended Song Name:", recommended_song_name)

    return jsonify({
        "recommended_song": recommended_song_name
    })
