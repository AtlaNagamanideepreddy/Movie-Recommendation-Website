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
from concurrent.futures import ThreadPoolExecutor, as_completed

# Suppress all warnings completely
if not sys.warnoptions:
    warnings.simplefilter("ignore")
logging.disable(logging.CRITICAL)

st.set_page_config(page_title="Movie Recommender", layout="wide", initial_sidebar_state="collapsed")

# Add advanced CSS with background image and animations
advanced_css = """
<style>
    /* Background with image */
    body {
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.8), rgba(20, 20, 40, 0.9)),
                    url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><defs><linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%%" style="stop-color:%23ff6b6b;stop-opacity:0.1" /><stop offset="100%%" style="stop-color:%2300ffff;stop-opacity:0.1" /></linearGradient></defs><rect width="100" height="100" fill="url(%23grad)"/></svg>');
        background-attachment: fixed;
        background-size: cover;
        color: #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Main container */
    .main {
        background: rgba(10, 10, 20, 0.7);
        backdrop-filter: blur(10px);
    }
    
    /* Header styling with subtle glow */
    h1, h2 {
        color: #ff6b6b;
        text-shadow: 0 0 20px rgba(255, 107, 107, 0.5);
    }
    
    /* Button styling with fast hover */
    .stButton > button {
        background: linear-gradient(135deg, #ff6b6b, #ff5252) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 5px 20px rgba(255, 107, 107, 0.4) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #ff5252, #ff3030) !important;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Selectbox styling */
    .stSelectbox {
        color: #e0e0e0;
    }
    
    .stSelectbox > div {
        border-color: #ff6b6b !important;
    }
    
    /* Movie title styling */
    .stText {
        color: #ffffff;
        font-weight: 700;
        text-align: center;
        margin-top: 0px;
        margin-bottom: 10px;
        font-size: 15px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        line-height: 1.4;
    }
    
    /* Image container with fast hover animation */
    .stImage {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.6);
        transition: all 0.2s ease;
        position: relative;
        max-height: 650px !important;
        margin-bottom: 15px;
    }
    
    .stImage:hover {
        transform: scale(1.08) translateY(-6px);
        box-shadow: 0 12px 35px rgba(255, 107, 107, 0.4);
    }
    
    .stImage img {
        transition: all 0.2s ease;
        width: 100% !important;
        height: auto !important;
        min-height: 380px !important;
    }
    
    .stImage:hover img {
        filter: brightness(1.1);
    }
    
    /* Column spacing */
    .stColumn {
        padding: 15px;
    }
    
    /* Info and warning messages */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid #ff6b6b;
        background: rgba(255, 107, 107, 0.1) !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(30, 30, 50, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #ff6b6b, #00ffff);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #ff5252, #00dddd);
    }
    
    /* Loading animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .loading {
        animation: pulse 1.5s ease-in-out infinite;
    }
</style>
"""

st.markdown(advanced_css, unsafe_allow_html=True)


def get_session_with_retries():
    """Create a requests session with retry strategy"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


@st.cache_resource(show_spinner=False)
def load_data():
    """Load movies and similarity data with caching"""
    try:
        movies = pickle.load(open('movie_list.pkl','rb'))
        similarity = pickle.load(bz2.open('similarity.pbz2','rb'))
        return movies, similarity
    except Exception as e:
        return None, None


@st.cache_data
def fetch_poster(movie_id):
    """Fetch poster from TMDB API with fast timeout"""
    api_keys = [
        "f2ed9dd1550b04f6306dd7be65808afb",
        "b0aa0a1b1d496d238c8917554ee42356"
    ]
    
    for api_key in api_keys:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        try:
            session = get_session_with_retries()
            response = session.get(url, timeout=3)
            response.raise_for_status()
            data = response.json()
            
            if 'status_code' in data and data['status_code'] != 200:
                continue
                
            poster_path = data.get('poster_path')
            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path
            else:
                return "https://via.placeholder.com/500x750?text=Movie&bgcolor=555&txtcolor=999"
                
        except:
            continue
    
    return "https://via.placeholder.com/500x750?text=Movie&bgcolor=555&txtcolor=999"

def recommend(movie, movies, similarity):
    if movie not in movies['title'].values:
        return [], []
    
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movie_names = []
    recommended_movie_posters = []
    
    # Get the 5 most similar movies
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].id
        movie_name = movies.iloc[i[0]].title
        recommended_movie_names.append(movie_name)
        recommended_movie_posters.append(movie_id)
    
    # Fetch all posters in parallel for speed
    final_posters = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(fetch_poster, recommended_movie_posters))
        final_posters = results
    
    return recommended_movie_names, final_posters


def main():
    # Title with animation
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 style="font-size: 56px; margin: 0; padding: 20px; color: #ff6b6b; text-shadow: 0 0 30px rgba(255, 107, 107, 0.6);">🎬 Movie Recommender</h1>
        <p style="color: #00ffff; font-size: 18px; margin: 10px 0; font-weight: 500;">Discover your next favorite movie</p>
    </div>
    """, unsafe_allow_html=True)
    
    movies, similarity = load_data()

    if movies is None or similarity is None:
        st.error("❌ Error loading data files.")
    else:
        # Search section
        st.markdown("<p style='color: #ff6b6b; font-weight: bold; font-size: 18px; margin-bottom: 15px;'>🔍 Select a movie:</p>", unsafe_allow_html=True)
        movie_list = movies['title'].values
        selected_movie = st.selectbox(
            "Movies",
            movie_list,
            label_visibility="collapsed"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button('🎯 Get Recommendations', use_container_width=True, key="rec_btn"):
                with st.spinner('🎬 Finding perfect matches...'):
                    recommended_movie_names, recommended_movie_posters = recommend(selected_movie, movies, similarity)
                    if not recommended_movie_names:
                        st.error("❌ Movie not found in database.")
                    else:
                        st.success(f"✨ Top 5 movies similar to **{selected_movie}**")
                        
                        # Display recommendations horizontally
                        st.markdown("<hr style='border-color: #ff6b6b; margin: 40px 0;'>", unsafe_allow_html=True)
                        
                        for idx, (name, poster) in enumerate(zip(recommended_movie_names, recommended_movie_posters)):
                            col_img, col_title = st.columns([2, 1])
                            
                            with col_img:
                                st.image(poster, width=300)
                            
                            with col_title:
                                st.write("")  # Spacer
                                st.markdown(f"<h4 style='color: #ff6b6b; font-size: 18px;'>{idx+1}. {name}</h4>", unsafe_allow_html=True)
                                st.write("⭐ Recommended for you")
                            
                            st.markdown("<hr style='border-color: #333; margin: 20px 0;'>", unsafe_allow_html=True)
                        
                        st.markdown("<hr style='border-color: #ff6b6b; margin: 40px 0;'>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style='text-align: center; margin-top: 60px; color: #888; font-size: 13px;'>
        <p>🎬 Movie Recommender System | Find your next favorite</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()