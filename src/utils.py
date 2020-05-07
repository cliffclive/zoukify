# # UTILITY FUNCTIONS FOR MUSIC CLASSIFIER TRAINING PIPELINE

import os, time, random, requests
import librosa, warnings
import numpy as np

import spotipy.oauth2 as oauth2
from dotenv import load_dotenv

mp3_dir = "data/mp3s"

def generate_token(username):
    """ Generate the token. Credentials are stored in .env file """
    load_dotenv('.env')
    
    # Cache for 'username' needs to be clear to load a new token.
    try:
        os.remove(f".cache-{username}")
    except:
        pass

    #scope = 'playlist-modify-public'
    credentials = oauth2.SpotifyClientCredentials(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"))
    token = credentials.get_access_token()
    return token


def identify_song(song_data):
    """ 
    Extracts a song's identifying tags from a Spotify metadata object
    Inputs:
        song_data : json/dict track metadata object from Spotify API
                    (ex: output of call to spotipy.track(track_id))
    Outputs:
        song_dict : dict with keys (id, artists, title, preview_url)
    """
    song_dict = {}
    song_dict['id'] = song_data['id']
    song_dict['artists'] = ', '.join([artist['name'] for 
                                      artist in song_data['artists']])
    song_dict['title'] = song_data['name']
    song_dict['preview_url'] = song_data['preview_url']
    return song_dict


def has_preview(song_data):
    """ 
    Returns True if a song's Spotify metadata contains a valid preview URL 
    Inputs:
        song_data : json/dict track metadata object from Spotify API
                    (ex: output of call to spotipy.track(track_id))
    Outputs:
        bool
    """
    preview = song_data['preview_url']
    if (type(preview)==str) and ('p.scdn.co' in preview):
        return True
    return False


def download_preview_mp3s(songs_list):
    """
    Downloads preview mp3s for a list of spotify track metadata dicts
    Inputs:
        songs_list : a list of track metadata dicts 
                     each must contain keys 'id' and 'preview_url'
    Outputs:
        none; saves downloaded mp3 samples in /mp3_dir (global variable)
    """
    global mp3_dir
    for song in songs_list:
        mp3_path = os.path.join(mp3_dir, song['id'] + ".mp3")
        if not os.path.isfile(mp3_path):
            time.sleep(random.random()/8)
            song_mp3 = requests.get(song['preview_url'], allow_redirects=True).content
            open(mp3_path, 'wb').write(song_mp3)


def extract_features(mp3_path):
    """
    Loads an mp3 file in librosa and extracts an audio feature array
    Inputs:
        mp3_path : path to desired mp3 file
    Outputs:
        y, sr    : audio time series and sample rate 
                   (returned by librosa.load)
        features : the audio features extracted by librosa 
                   (currently just the melspectrogram)
    """
    # Suppress "UserWarning: PySoundFile failed. Trying audioread instead."
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        y, sr = librosa.load(mp3_path)
    features = librosa.feature.melspectrogram(y, sr)
    return y, sr, features


def build_features_array(songs, max_ts=1294):
    """
    Builds an array of audio features, generated by the extract_features function,
    for a list of song metadata dictionaries.
    Inputs:
        songs : list of spotify track metadata dicts ('id' key required)
    Outputs:
        data  : numpy array with dimensions i, j, k
                - data[i] = audio features for songs[i]
                - j, k = shape of audio features array
                - j = audio sample at time j
                - k = features for audio sample
    """
    song_id = songs[0]['id']
    mp3_path = os.path.join(mp3_dir, song_id + ".mp3")
    y, sr, feats = extract_features(mp3_path)
    if not max_ts:
        max_ts = feats.shape[1]
    data = np.zeros([len(songs), feats.shape[0], max_ts])
    for i, song in enumerate(songs):
        song_id = song['id']
        mp3_path = os.path.join(mp3_dir, song_id + ".mp3")
        y, sr, feats = extract_features(mp3_path)
        ts = min(feats.shape[1], max_ts)
        data[i,:,:ts] = feats[:,:ts]
        
    return data
