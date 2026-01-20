import pickle
import streamlit as st
import requests
from PIL import Image
import bz2
import warnings
import logging
import os
import sys
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Suppress all warnings completely
if not sys.warnoptions:
    warnings.simplefilter("ignore")
logging.disable(logging.CRITICAL)

st.set_page_config(page_title="Movie Recommender", layout="wide")

# Add custom CSS
try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    st.markdown("""
    <style>
    body {
        background-color: #1a1a1a;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def load_data():
    """Load movies and similarity data with caching"""
    try:
        movies = pickle.load(open('movie_list.pkl','rb'))
        similarity = pickle.load(bz2.open('similarity.pbz2','rb'))
        return movies, similarity
    except Exception as e:
        return None, None


def get_placeholder_image(title):
    """Generate a placeholder image with movie title"""
    return f"https://via.placeholder.com/500x750?text={title.replace(' ', '+')}&bgcolor=444&txtcolor=fff"


def recommend(movie, movies, similarity):
    if movie not in movies['title'].values:
        return [], []
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_images = []
    for i in distances[1:6]:
        movie_title = movies.iloc[i[0]].title
        recommended_movie_names.append(movie_title)
        # Use placeholder with movie name
        recommended_movie_images.append(get_placeholder_image(movie_title))

    return recommended_movie_names, recommended_movie_images


def main():
    st.write("## Watch your favourite movies:- ")
    st.header('Movie Recommender System')
    
    st.info("⚠️ Using placeholder images (Network connection issue detected)")
    st.write("*Your system cannot access external APIs. Showing text-based placeholders.*")
    
    movies, similarity = load_data()

    if movies is None or similarity is None:
        st.error("Error loading data files. Please ensure movie_list.pkl and similarity.pbz2 are present and valid.")
    else:
        movie_list = movies['title'].values
        selected_movie = st.selectbox(
            "Type or select a movie from the dropdown",
            movie_list
        )

        if st.button('Show Recommendation'):
            recommended_movie_names, recommended_movie_images = recommend(selected_movie, movies, similarity)
            if not recommended_movie_names:
                st.error("Movie not found in database.")
            else:
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.text(recommended_movie_names[0])
                    st.image(recommended_movie_images[0], use_column_width=True)
                with col2:
                    st.text(recommended_movie_names[1])
                    st.image(recommended_movie_images[1], use_column_width=True)
                with col3:
                    st.text(recommended_movie_names[2])
                    st.image(recommended_movie_images[2], use_column_width=True)
                with col4:
                    st.text(recommended_movie_names[3])
                    st.image(recommended_movie_images[3], use_column_width=True)
                with col5:
                    st.text(recommended_movie_names[4])
                    st.image(recommended_movie_images[4], use_column_width=True)


if __name__ == "__main__":
    main()
