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
import json
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Suppress all warnings completely
if not sys.warnoptions:
    warnings.simplefilter("ignore")
logging.disable(logging.CRITICAL)

st.set_page_config(page_title="Movie Recommender Pro", layout="wide", initial_sidebar_state="expanded")

# Advanced CSS
advanced_css = """
<style>
    body {
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.8), rgba(20, 20, 40, 0.9)),
                    url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><defs><linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%%" style="stop-color:%23ff6b6b;stop-opacity:0.1" /><stop offset="100%%" style="stop-color:%2300ffff;stop-opacity:0.1" /></linearGradient></defs><rect width="100" height="100" fill="url(%23grad)"/></svg>');
        background-attachment: fixed;
        color: #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main {
        background: rgba(10, 10, 20, 0.7);
        backdrop-filter: blur(10px);
    }
    
    h1, h2 {
        color: #ff6b6b;
        text-shadow: 0 0 20px rgba(255, 107, 107, 0.5);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #ff6b6b, #ff5252) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        font-weight: 700 !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 5px 20px rgba(255, 107, 107, 0.4) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #ff5252, #ff3030) !important;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    .stImage {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.6);
        transition: all 0.2s ease;
    }
    
    .stImage:hover {
        transform: scale(1.08) translateY(-6px);
        box-shadow: 0 12px 35px rgba(255, 107, 107, 0.4);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 107, 107, 0.2) !important;
        border-radius: 8px !important;
        color: #fff !important;
        padding: 12px 24px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ff6b6b, #ff5252) !important;
    }
    
    .chat-message {
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
    }
    
    .chat-user {
        background: rgba(255, 107, 107, 0.2);
        border-left: 4px solid #ff6b6b;
    }
    
    .chat-bot {
        background: rgba(0, 255, 255, 0.1);
        border-left: 4px solid #00ffff;
    }
</style>
"""

st.markdown(advanced_css, unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'saved_recommendations' not in st.session_state:
    st.session_state.saved_recommendations = []

if 'ratings' not in st.session_state:
    st.session_state.ratings = {}

if 'last_recommendations' not in st.session_state:
    st.session_state.last_recommendations = []

if 'last_searched_movie' not in st.session_state:
    st.session_state.last_searched_movie = ""

if 'show_recommendations' not in st.session_state:
    st.session_state.show_recommendations = False

if 'last_posters' not in st.session_state:
    st.session_state.last_posters = []

# File paths
SAVED_FILE = "saved_recommendations.json"
RATINGS_FILE = "movie_ratings.json"

# Configure Gemini API
def setup_gemini():
    """Setup Gemini API with key from sidebar"""
    try:
        gemini_key = st.secrets.get("GEMINI_API_KEY", None)
        if not gemini_key:
            return False
        genai.configure(api_key=gemini_key)
        return True
    except:
        return False

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
    """Load movies and similarity data"""
    try:
        movies = pickle.load(open('movie_list.pkl','rb'))
        similarity = pickle.load(bz2.open('similarity.pbz2','rb'))
        return movies, similarity
    except:
        return None, None

@st.cache_data
def fetch_poster(movie_id):
    """Fetch poster from TMDB API"""
    api_keys = [
        "f2ed9dd1550b04f6306dd7be65808afb",
        "b0aa0a1b1d496d238c8917554ee42356"
    ]
    
    for api_key in api_keys:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        try:
            session = get_session_with_retries()
            response = session.get(url, timeout=3)
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
    """Get recommendations"""
    if movie not in movies['title'].values:
        return [], []
    
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    names = []
    movie_ids = []
    
    for i in distances[1:6]:
        names.append(movies.iloc[i[0]].title)
        movie_ids.append(movies.iloc[i[0]].id)
    
    posters = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(fetch_poster, movie_ids))
        posters = results
    
    return names, posters

# Chatbot functions
def get_movie_info(movie_name, movies):
    """Get info about a movie"""
    if movie_name.lower() in movies['title'].str.lower().values:
        movie = movies[movies['title'].str.lower() == movie_name.lower()].iloc[0]
        return f"Found: **{movie['title']}** (ID: {movie['id']})"
    return "Movie not found in database."

def chat_response(user_message, movies):
    """Generate chatbot response with real movie names"""
    user_msg_lower = user_message.lower()
    
    # Always provide real movie suggestions
    try:
        # Get random sample of movies
        sample_movies = movies.sample(min(5, len(movies)))['title'].tolist()
        sample_text = ', '.join(sample_movies)
        
        # Try Gemini API
        try:
            if setup_gemini():
                prompt = f"""Give a SHORT 1-2 sentence response. Mention these movies when relevant: {sample_text}
Question: {user_message}
Be friendly and mention specific movies!\"""
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt, generation_config={'temperature': 0.7, 'max_output_tokens': 100})
                if response.text:
                    return response.text.strip()
        except:
            pass
        
        # Fallback: provide real movie suggestions
        if any(word in user_msg_lower for word in ['recommend', 'suggest', 'good', 'movie', 'watch', 'like']):
            return f"🎬 Try these: **{sample_text}**\n\nUse 🎯 **Recommender** to find similar ones!"
        else:
            return f"I can help! 🎬 Ask me about movies or use **Recommender** to find great films!"
    except:
        return "🎬 Ask me about movies or use the **Recommender** tab!"

# Save/Load recommendations
def save_recommendation(movie_name, recommendations):
    """Save recommendations to file"""
    try:
        # Ensure recommendations is a list
        if not isinstance(recommendations, list):
            recommendations = list(recommendations)
        
        # Load existing data
        if os.path.exists(SAVED_FILE):
            with open(SAVED_FILE, 'r') as f:
                data = json.load(f)
        else:
            data = []
        
        # Append new recommendation
        data.append({
            'timestamp': datetime.now().isoformat(),
            'searched_movie': movie_name,
            'recommendations': recommendations
        })
        
        # Save to file
        with open(SAVED_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving recommendation: {e}")
        return False

def load_saved_recommendations():
    """Load saved recommendations"""
    try:
        if os.path.exists(SAVED_FILE):
            with open(SAVED_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

# Rating functions
def save_rating(movie_name, rating):
    """Save movie rating"""
    try:
        if os.path.exists(RATINGS_FILE):
            with open(RATINGS_FILE, 'r') as f:
                data = json.load(f)
        else:
            data = {}
        
        data[movie_name] = rating
        
        with open(RATINGS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except:
        return False

def load_ratings():
    """Load ratings"""
    try:
        if os.path.exists(RATINGS_FILE):
            with open(RATINGS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

# Email function
def send_email(recipient_email, movie_names, sender_email="your_email@gmail.com", sender_password="your_app_password"):
    """Send recommendations via email"""
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Your Movie Recommendations"
        message["From"] = sender_email
        message["To"] = recipient_email
        
        movie_list_html = ''.join([f'<li style="margin: 10px 0; font-size: 16px;">{movie}</li>' for movie in movie_names])
        html = f"""<html>
            <body style="font-family: Arial; background: #0f0f0f; color: #fff; padding: 20px;">
                <h1 style="color: #ff6b6b;">Movie Recommendations</h1>
                <p>Here are your personalized movie recommendations:</p>
                <ul>
                    {movie_list_html}
                </ul>
                <p style="margin-top: 30px; color: #888;">Enjoy the movies!</p>
            </body>
        </html>
        """
        
        part = MIMEText(html, "html")
        message.attach(part)
        
        # Note: This requires setting up email credentials
        # For demo, just return True
        return True
    except:
        return False

# Main app
def main():
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 style="font-size: 56px; margin: 0; padding: 20px;">Movie Recommender Pro</h1>
        <p style="color: #00ffff; font-size: 18px; margin: 10px 0;">AI-Powered Recommendations + Chat + Save + Rate</p>
    </div>
    """, unsafe_allow_html=True)
    
    movies, similarity = load_data()
    
    if movies is None or similarity is None:
        st.error("❌ Error loading data files.")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Recommender", "💬 Chat", "💾 Saved", "⭐ Ratings"])
    
    # ==================== TAB 1: RECOMMENDER ====================
    with tab1:
        st.markdown("<h2 style='color: #ff6b6b;'>Find Your Next Favorite Movie</h2>", unsafe_allow_html=True)
        
        movie_list = movies['title'].values
        selected_movie = st.selectbox("🔍 Select a movie:", movie_list, label_visibility="collapsed", key="search_movie")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button('🎯 Get Recommendations', use_container_width=True):
                with st.spinner('🎬 Finding perfect matches...'):
                    names, posters = recommend(selected_movie, movies, similarity)
                    
                    # Store in session state
                    st.session_state.last_recommendations = list(names) if hasattr(names, '__iter__') else names
                    st.session_state.last_searched_movie = selected_movie
                    st.session_state.show_recommendations = True
                    st.session_state.last_posters = posters
                    
                    if not names:
                        st.error("❌ No recommendations found.")
        
        # Display recommendations OUTSIDE spinner so Save button is always visible
        if st.session_state.get('show_recommendations', False) and st.session_state.get('last_recommendations'):
            st.success(f"✨ Top 5 movies similar to **{st.session_state.last_searched_movie}**")
            st.markdown("<hr style='border-color: #ff6b6b; margin: 40px 0;'>", unsafe_allow_html=True)
            
            for idx, (name, poster) in enumerate(zip(st.session_state.last_recommendations, st.session_state.get('last_posters', []))):
                col_img, col_info = st.columns([2, 1])
                
                with col_img:
                    st.image(poster, width=300)
                
                with col_info:
                    st.write("")
                    st.markdown(f"<h4 style='color: #ff6b6b; font-size: 18px;'>{idx+1}. {name}</h4>", unsafe_allow_html=True)
                    
                    col_rate, col_save = st.columns(2)
                    with col_rate:
                        if st.button(f"⭐ Rate", key=f"rate_{idx}"):
                            st.session_state.show_rating = True
                    
                    with col_save:
                        if st.button(f"💾 Save", key=f"save_{idx}"):
                            success = save_recommendation(st.session_state.last_searched_movie, st.session_state.last_recommendations)
                            if success:
                                st.success(f"✅ Saved!")
                                st.balloons()
                            else:
                                st.error("❌ Save failed")
                
                st.markdown("<hr style='border-color: #333; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # ==================== TAB 2: CHATBOT ====================
    with tab2:
        st.markdown("<h2 style='color: #ff6b6b;'>Movie Chat Assistant</h2>", unsafe_allow_html=True)
        
        # Display chat history using Streamlit's chat UI
        for message in st.session_state.chat_history:
            with st.chat_message("user" if message['role'] == 'user' else "assistant"):
                st.markdown(message['content'])
        
        # Chat input
        user_input = st.chat_input("💬 Ask me about movies...")
        
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            
            # Generate bot response
            response = chat_response(user_input, movies)
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            
            # Rerun to display new messages
            st.rerun()
    
    # ==================== TAB 3: SAVED ====================
    with tab3:
        st.markdown("<h2 style='color: #ff6b6b;'>Your Saved Recommendations</h2>", unsafe_allow_html=True)
        
        # Add refresh button
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        saved = load_saved_recommendations()
        
        if saved:
            st.success(f"✅ {len(saved)} saved recommendation(s)")
            
            for idx, item in enumerate(saved):
                with st.container():
                    st.write(f"📅 **Date:** {item['timestamp'][:10]}")
                    st.write(f"🎬 **Searched for:** {item['searched_movie']}")
                    st.write(f"**📋 Recommendations:**")
                    
                    # Create columns for better display
                    cols = st.columns(2)
                    for i, rec in enumerate(item['recommendations']):
                        with cols[i % 2]:
                            st.write(f"• {rec}")
                    
                    # Delete button
                    if st.button(f"🗑️ Delete", key=f"delete_{idx}"):
                        saved.pop(idx)
                        with open(SAVED_FILE, 'w') as f:
                            json.dump(saved, f, indent=2)
                        st.success("✅ Deleted!")
                        st.rerun()
                    
                    st.markdown("<hr style='border-color: #ff6b6b; opacity: 0.3;'>", unsafe_allow_html=True)
        else:
            st.info("📭 No saved recommendations yet!\n\n1. Go to 🎯 **Recommender** tab\n2. Select a movie\n3. Click **Get Recommendations**\n4. Click 💾 **Save** on any recommendation")
    
    # ==================== TAB 4: RATINGS ====================
    with tab4:
        st.markdown("<h2 style='color: #ff6b6b;'>Rate Your Movies</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            movie_to_rate = st.selectbox("🎬 Select a movie to rate:", movie_list, key="rate_movie")
        
        with col2:
            rating = st.slider("⭐ Rating:", 1, 10, 5, key="rating_slider")
        
        if st.button("💾 Save Rating", use_container_width=True):
            if save_rating(movie_to_rate, rating):
                st.success(f"✅ Rated **{movie_to_rate}** as {rating}/10")
            else:
                st.error("❌ Failed to save rating")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write("### 📊 Your Ratings")
        
        ratings = load_ratings()
        if ratings:
            for movie, rating in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
                st.write(f"⭐ **{movie}**: {rating}/10")
        else:
            st.info("No ratings yet. Start rating movies!")
    
    # Footer
    st.markdown("""
    <div style='text-align: center; margin-top: 60px; color: #888; font-size: 13px; border-top: 1px solid #333; padding-top: 20px;'>
        <p>Movie Recommender Pro | Full-Featured Recommendation Engine</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
