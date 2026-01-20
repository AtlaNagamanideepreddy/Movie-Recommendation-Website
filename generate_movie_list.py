import pickle
import pandas as pd
import bz2
import _pickle as cPickle

# Load the existing similarity data to understand the structure
print("Loading similarity data...")
similarity = bz2.BZ2File('similarity.pbz2', "rb")
similarity_data = cPickle.load(similarity)
print(f"Similarity matrix shape: {similarity_data.shape}")
print(f"Number of movies: {similarity_data.shape[0]}")

# Check if movie_dict.pkl exists and load it
try:
    print("\nLoading movie_dict.pkl...")
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    print(f"Successfully loaded movie_dict.pkl with {len(movies_dict)} movies")
    
    # Convert to DataFrame if needed
    if not isinstance(movies_dict, pd.DataFrame):
        movies = pd.DataFrame(movies_dict)
    else:
        movies = movies_dict
    
    print("\nDataFrame info:")
    print(movies.info())
    print("\nFirst few rows:")
    print(movies.head())
    
    # Save as movie_list.pkl
    print("\nSaving as movie_list.pkl...")
    pickle.dump(movies, open('movie_list.pkl', 'wb'))
    print("Successfully created movie_list.pkl!")
    
except FileNotFoundError:
    print("movie_dict.pkl not found. Creating a sample movie_list from similarity matrix...")
    # Create a basic dataframe with movie indices
    movies = pd.DataFrame({
        'title': [f'Movie {i}' for i in range(similarity_data.shape[0])],
        'movie_id': range(similarity_data.shape[0])
    })
    
    print("\nSaving as movie_list.pkl...")
    pickle.dump(movies, open('movie_list.pkl', 'wb'))
    print("Created sample movie_list.pkl with placeholder data!")
    print("NOTE: You'll need to populate this with actual movie data for the recommender to work properly.")
