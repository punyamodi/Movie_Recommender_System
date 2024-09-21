# Movie_Recommender_System

LIVE URL - https://bo6fqwrhupbw9c728dsf2d.streamlit.app/

This is a movie recommender system built using Python and various machine learning libraries. It utilizes content-based filtering to make movie recommendations based on similarity of movie tags.

<img width="1280" alt="image" src="https://github.com/punyamodi/Movie_Recommender_System/assets/68418104/10778d27-5eab-4fa7-9409-f67081134891">

## Data Preprocessing
The raw data is obtained from the TMDB 5000 Movie Dataset. It contains details like cast, crew, genres, keywords, and overviews for 5000 movies.

The data is preprocessed to extract relevant features, clean text, stem words, and create a unified 'tags' column for each movie. This contains the crucial information that will be used to calculate similarity between movies.

## Model Building
The 'tags' text data is vectorized using CountVectorizer, which converts text into feature vectors. Then cosine similarity scores are calculated between all movie vectors to quantify similarity.

## Recommendations
To generate recommendations for a movie, we find its index and fetch the similarity scores of that movie with all others. The top 10 most similar movies are recommended based on the similarity scores.

## Saving Models
The preprocessed movie dataframe, dictionary, and similarity matrix are serialized using pickle. This allows the models to be easily loaded later for generating recommendations.

## Deployment
The recommender system is deployed using Streamlit for an interactive web-based interface. Users can select movies and instantly see recommendations. The pickled models are loaded and predictions are made on the fly.

<img width="1280" alt="image" src="https://github.com/punyamodi/Movie_Recommender_System/assets/68418104/3beebd72-2448-4b48-9535-83cd198df756">
