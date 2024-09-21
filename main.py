import pickle
import streamlit as st
import requests
import pandas as pd

# Function to download a file from a URL
def download_file(url, destination):
    response = requests.get(url)
    with open(destination, 'wb') as file:
        file.write(response.content)

# Google Drive link to 'movies_dict.pkl' (replace with your actual link)
movies_dict_url = 'https://drive.google.com/uc?export=download&id=1HCNOOnP4NgsKPb6qGqfbr-ekjx08VsvI'

# Local path to save the downloaded file
movies_dict_path = 'movies_dict.pkl'

# Download the file from Google Drive
download_file(movies_dict_url, movies_dict_path)

# Load the downloaded pickle file
with open('movie_list.pkl', 'rb') as f:
    movies = pd.read_pickle("movie_list.pkl")

with open(movies_dict_path, 'rb') as f:
    similarity = pickle.load(f)

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=bfb2634dae4592761658dba50f11ec8f&language=en-US".format(movie_id)
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    if poster_path:
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    return None

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:16]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters

# Streamlit app UI
st.header('Movie Recommender System')

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    
    # Display recommendations
    cols = st.columns(5)
    for idx in range(15):
        col = cols[idx % 5]
        with col:
            st.text(recommended_movie_names[idx])
            st.image(recommended_movie_posters[idx])
