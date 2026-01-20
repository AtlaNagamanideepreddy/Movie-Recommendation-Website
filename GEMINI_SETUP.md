# Setup Guide for Movie Recommender with Gemini AI

## Step 1: Get Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your API key

## Step 2: Add API Key to Secrets

Edit `.streamlit/secrets.toml` and replace:
```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

With your actual API key:
```toml
GEMINI_API_KEY = "your-actual-api-key-here"
```

## Step 3: Install Gemini Package

```bash
pip install google-generativeai==0.7.2
```

## Step 4: Run the App

```bash
streamlit run app_enhanced.py
```

## Features

✅ **AI Chatbot** - Uses Gemini 2.5 Flash for intelligent responses
✅ **Save Movies** - Save your favorite recommendations (FIXED!)
✅ **Rate Movies** - Rate movies 1-10
✅ **Movie Recommendations** - Get 5 similar movies
✅ **4,801 Movies** - Browse a large database

## Chat Examples

Try asking:
- "What's a good movie to watch?"
- "Tell me about Avatar"
- "How do I save recommendations?"
- "Can you recommend a comedy?"
- "What's the best sci-fi movie?"

The chatbot uses Gemini 2.5 Flash and has access to your movie database!
