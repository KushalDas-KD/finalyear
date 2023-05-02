import streamlit as st
import pandas as pd
import pickle
from fuzzywuzzy import fuzz
from recommender import hybrid_recommend, get_metadata
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

dataset_url = 'https://www.kaggle.com/datasets/imuhammad/audio-features-and-lyrics-of-spotify-songs'

st.set_page_config(
    page_title='Zingged', 
    page_icon='🎶',
    menu_items={
        'Get Help': None,
        'About': f"### Project made as a Final Year Project!\n#### Music Data sourced from [Kaggle]({dataset_url})"
    }
)

st.title('🎶 ZINGGED 🎶')
search_term = st.session_state.get('search_term', '')  # Get the current value of the search term, or an empty string if it hasn't been set
data = pickle.load(open('pickles/data.pkl', 'rb'))
# Create the search box and search button
search_box = st.text_input("Search Song", value=search_term, key="search_box")
search_button = st.button("Search")

def find_closest_match(search_term, data_column):
    closest_match = data_column.str.lower().str.contains(search_term.lower()).idxmax()
    return closest_match

if search_button:
    search_term = search_box.strip()  # Get the trimmed value of the search box
    closest_index = find_closest_match(search_term, data['track_name'])
    st.session_state['current_song_index'] = closest_index
    st.session_state['search_term'] = ''  # Set the search term to an empty string after the search button is clicked
    


        
# Persistent app state managment

def change_song(index):
    st.session_state['current_song_index'] = index

if 'current_song_index' not in st.session_state:
    change_song(1255)





# Sidebar with customizing options

st.sidebar.title('Choose:')

option1 = 'Keep up with what\'s trending'
option2 = 'Discover hidden gems'
mode = st.sidebar.selectbox('Your mode of recommendations', (option1, option2))
if(mode == option1):
    prioritisePopular = True
else:
    prioritisePopular = False

recommendations_count = st.sidebar.slider('Upto how many of each kind of recommendations would you like '
'(lesser means more accurate but more means more variety!)', min_value=1, max_value=10, value=3)

st.sidebar.write('Which kinds of recommendations you\'d like') # options added later below when adding songs



# Main Content:
SPOTIFY_CLIENT_ID = 'c7b43b3a7816424c9ce08996bb5e6fc0'
SPOTIFY_CLIENT_SECRET = '0a9abfd75f814a2499642ebfa7d01895'
client_credentials_manager = SpotifyClientCredentials(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Showing current song
current_song = get_metadata(st.session_state['current_song_index'])
song_id= change_song
results = sp.search(q=f"track:{song_id}", type="track", limit=1)


song_name = current_song["track_name"]
artist_name = current_song["track_artist"]

# Search for the song on Spotify
query = f"track:{song_name} artist:{artist_name}"
results = sp.search(q=query, type='track')

# Extract the Spotify ID from the search results
if results['tracks']['total'] > 0:
    spotify_id = results['tracks']['items'][0]['id']


spotify_uri = 'spotify:track:' + spotify_id
spotify_url = f"https://open.spotify.com/embed/track/{spotify_uri.split(':')[-1]}"
st.components.v1.iframe(spotify_url, width=300, height=380)

st.write(f'## {current_song["track_name"]} - {current_song["track_artist"]}')


with st.expander('Show lyrics'):
    st.write(current_song['lyrics'])


# Retreiving and showing recommendations as per user's choices

recommendations = hybrid_recommend(st.session_state['current_song_index'], recommendations_count, prioritisePopular=prioritisePopular)

for recommendation_type, songs in recommendations.items():
    if not st.sidebar.checkbox(recommendation_type, value=True):
        continue
    if(len(songs) == 0): # do not show a recommendation type if it has no songs
        continue
    st.write(f'#### {recommendation_type.title()}')
    with st.container():
        for song in songs:
            st.write(f'- {song["track_name"]} - {song["track_artist"]}')
            song_name = song["track_name"]
            artist_name = song["track_artist"]

            # Search for the song on Spotify
            query = f"track:{song_name} artist:{artist_name}"
            results = sp.search(q=query, type='track')

            # Extract the Spotify ID from the search results
            if results['tracks']['total'] > 0:
                spotify_id = results['tracks']['items'][0]['id']
                thumbnail_url = results['tracks']['items'][0]['album']['images'][0]['url']
                st.image(thumbnail_url, width=300)
            
            st.button("listen", key=str(song['index'])+recommendation_type, on_click=change_song, args=(song['index'],))
