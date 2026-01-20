# Movie Recommender System - Image Setup Guide

## Current Status
✅ Movie data is loaded
✅ Similarity matrix is working
✅ Background styling is applied

## Image Sources

The app fetches movie posters from **TMDB (The Movie Database) API** automatically. Here's what you need to know:

### How Posters Are Fetched
1. When you select a movie and click "Show Recommendation"
2. The app gets the movie ID from your database
3. It queries the TMDB API to get the poster URL
4. The poster is displayed in real-time

### Troubleshooting Image Issues

#### If posters aren't showing:

**Option 1: Check Internet Connection**
- Make sure you have a stable internet connection
- The app downloads posters from `https://image.tmdb.org/t/p/w500/`

**Option 2: Verify API Access**
- The app uses TMDB API keys to fetch movie data
- If you keep getting gray placeholders, the API key might be rate-limited
- Contact TMDB to get your own API key: https://www.themoviedb.org/settings/api

**Option 3: Use Local Poster Images**
If you want to use local images instead, create a `posters/` folder:

```
newmovie/
├── app.py
├── posters/
│   ├── 19995.jpg (Avatar)
│   ├── 285.jpg (Pirates of the Caribbean)
│   └── ...
```

Then modify the `fetch_poster()` function in `app.py` to:
```python
def fetch_poster(movie_id):
    """Fetch poster from local folder or TMDB API"""
    # Try local file first
    local_path = f"posters/{movie_id}.jpg"
    if os.path.exists(local_path):
        return local_path
    
    # Fall back to TMDB API...
    # (rest of the function)
```

### Current Styling

The app now includes:
- **Dark theme** with movie industry vibes
- **Red accent color** (#ff6b6b) for buttons and headers
- **Hover effects** on images for better interactivity
- **Smooth transitions** and animations
- **Responsive design** that works on mobile and desktop

### Files Modified

1. **app.py** - Enhanced with better error handling and CSS integration
2. **style.css** - Updated with modern dark theme and effects

### Next Steps

1. **Run the app:**
   ```bash
   streamlit run app.py
   ```

2. **If images still don't load:**
   - Check your internet connection
   - Wait a few seconds (API responses can be slow)
   - Check the browser console for errors (F12)

3. **For better performance:**
   - The app caches poster URLs, so they'll load faster after first load
   - Clear cache if you want to refresh images: `Ctrl+F` and search "Clear cache" in Streamlit menu

## Need Your Own TMDB API Key?

1. Go to https://www.themoviedb.org/settings/api
2. Create an account and get your free API key
3. Replace the API keys in `app.py` line 73-76 with your own

---

**Happy movie watching! 🎬**
