# 🎬 Movie Recommender Pro

An intelligent movie recommendation system with AI chatbot, rating system, and recommendation saving.

## ✨ Features

- **🎯 Smart Recommendations** - AI-powered similar movie suggestions
- **💬 Chatbot** - Discuss movies and get recommendations
- **💾 Save Recommendations** - Store your favorite recommendation sets
- **⭐ Rating System** - Rate movies and track your preferences
- **📧 Email Integration** - Send recommendations via email
- **🌐 Fast Performance** - Optimized for speed with parallel processing

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone or download the project:**
```bash
cd newmovie
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Ensure data files are present:**
```
newmovie/
├── app_enhanced.py
├── movie_list.pkl
├── similarity.pbz2
└── requirements.txt
```

4. **Run the app:**
```bash
streamlit run app_enhanced.py
```

5. **Open in browser:**
```
http://localhost:8501
```

---

## 🌐 Deploy to Streamlit Cloud (FREE - RECOMMENDED)

### Step 1: Prepare Your Project

1. **Create a GitHub account** (if you don't have one): https://github.com/signup

2. **Create a new GitHub repository:**
   - Go to https://github.com/new
   - Repository name: `movie-recommender-pro`
   - Make it **Public**
   - Click "Create repository"

3. **Upload your project files to GitHub:**
   - You'll see instructions to upload files
   - Upload these files:
     - `app_enhanced.py`
     - `movie_list.pkl`
     - `similarity.pbz2`
     - `requirements.txt`
     - `.streamlit/config.toml`
     - `README.md`

### Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud:** https://streamlit.io/cloud

2. **Click "Deploy an app"**

3. **Sign in with GitHub** (if you haven't already)

4. **Fill in the deployment form:**
   - GitHub repo: `your-username/movie-recommender-pro`
   - Branch: `main`
   - Main file path: `app_enhanced.py`

5. **Click "Deploy"** ✨

6. **Wait 2-3 minutes** for deployment

7. **Your app is live!** Share the URL with others

### Your Public URL will look like:
```
https://movie-recommender-pro-yourname.streamlit.app
```

---

## 📱 Alternative Deployment Options

### Heroku (Paid - $7/month)
1. Create account: https://heroku.com
2. Create `Procfile`:
   ```
   web: streamlit run app_enhanced.py
   ```
3. Deploy using Heroku CLI

### Railway (Paid - $5 credits/month)
1. Create account: https://railway.app
2. Connect GitHub repo
3. Select `app_enhanced.py` as entrypoint

### Replit (Free)
1. Go to https://replit.com
2. Create new Repl from GitHub
3. Paste your repo URL
4. Run `streamlit run app_enhanced.py`

---

## 🎮 How to Use

### Recommender Tab
1. Select a movie from the dropdown
2. Click "Get Recommendations"
3. Browse 5 similar movies
4. Rate or Save recommendations

### Chat Tab
1. Type your question about movies
2. Get instant AI responses
3. Chat history is saved in session

### Saved Tab
1. View all your saved recommendations
2. Check timestamps
3. Delete old saves

### Ratings Tab
1. Select a movie
2. Give it a rating (1-10)
3. View all your ratings sorted by score

---

## 📊 Data Files

- **movie_list.pkl** - 4,801 movies database
- **similarity.pbz2** - Movie similarity matrix for recommendations

## 🔧 Customization

### Change Colors
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#ff6b6b"  # Change this color
```

### Add Email Support
Edit the `send_email()` function in `app_enhanced.py` and add your Gmail credentials.

### Add More Movies
Replace `movie_list.pkl` and `similarity.pbz2` with your custom dataset.

---

## 🐛 Troubleshooting

### "Error loading data files"
- Ensure `movie_list.pkl` and `similarity.pbz2` are in the same directory as app
- Check file permissions

### "Connection error" on image loading
- Network issue with TMDB API
- Images will show placeholders
- App still works normally

### Slow performance
- Wait for initial load (data caching)
- Subsequent searches are faster
- Deploy to Streamlit Cloud for better performance

---

## 📧 Email Setup (Optional)

1. Enable 2FA on your Gmail: https://myaccount.google.com/security
2. Create App Password: https://myaccount.google.com/app-passwords
3. Add to `app_enhanced.py`:
```python
sender_email = "your_email@gmail.com"
sender_password = "your_16_char_password"
```

---

## 📝 Files Structure

```
movie-recommender-pro/
├── app_enhanced.py              # Main enhanced app
├── app.py                       # Original simple app
├── movie_list.pkl               # Movie database
├── similarity.pbz2              # Similarity matrix
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── .streamlit/
│   └── config.toml             # Streamlit config
├── saved_recommendations.json   # Auto-created (saves)
└── movie_ratings.json          # Auto-created (ratings)
```

---

## 🤝 Contributing

Want to improve this app? 
1. Fork the repository
2. Make changes
3. Submit a pull request

---

## 📄 License

This project is open source and available for everyone to use and modify.

---

## 🎬 Share Your App!

Once deployed, share the Streamlit Cloud URL with:
- Friends and family
- Social media
- Communities
- Anywhere you want!

### Example Sharing Text:
```
🎬 Check out my AI-powered Movie Recommender!
Discover movies you'll love with personalized recommendations, 
chat with the bot, save your favorites, and rate films!

👉 [Your Streamlit App URL]
```

---

## 📞 Support

If you have issues:
1. Check the Troubleshooting section
2. Review Streamlit docs: https://docs.streamlit.io
3. Check GitHub issues

---

**Enjoy recommending movies! 🍿✨**
