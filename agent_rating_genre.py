import pandas as pd
from sqlalchemy import create_engine
from sklearn.metrics.pairwise import cosine_similarity
from agent_rating import get_movie_recommendations
from agent_genre import get_genre_recommendations

# Etape 1: Extraction
# Charger les fichiers CSV
column_names = ['user_id', 'item_id', 'rating', 'timestamp']
u_data = pd.read_csv('u.data', sep='\t', names=column_names)
movie_id_title = pd.read_csv("Movie_Id_Titles")

# Etape 2: Transformation
# Fusionner les données pour obtenir le titre des films
merged_data = pd.merge(u_data, movie_id_title, on='item_id')

# Etape 3: Chargement
# Charger les données dans une base de données (SQLite par exemple)
engine = create_engine('sqlite:///movie_recommendation.db')

# Charger les données transformées dans la base de données
merged_data.to_sql('movie_ratings', engine, if_exists='replace', index=False)

################# OLAP
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Assuming you have the 'merged_data' DataFrame and 'cube' DataFrame as defined in your question.

# Define dimensions and measures
dimensions = ['user_id', 'item_id']
measures = ['rating']

# Create a multi-dimensional DataFrame (OLAP cube)
cube = merged_data.groupby(dimensions)[measures].sum()


# Define a function to get movie recommendations based on genre and ratings
def get_movie_recommendations_by_genre_and_rating(movie_id, cube):
    # Get recommendations based on ratings
    recommendations_by_rating = get_movie_recommendations(movie_id, cube)

    # Extract genres for the given movie from the DataFrame 'cube'
    movie_genres = merged_data[merged_data['item_id'] == movie_id]['genres'].values
    if len(movie_genres) == 0:
        return []  # Movie has no genre information, return an empty list

    movie_genres = movie_genres[0].split('|')

    # Clean data: Remove rows with missing values in 'genres' column
    merged_data_cleaned = merged_data.dropna(subset=['genres'])

    # Find movies with similar genres
    similar_movies = []

    for genre in movie_genres:
        cube_filtered = merged_data_cleaned[merged_data_cleaned['genres'].str.contains(genre)]
        similar_movies.extend(cube_filtered['item_id'].tolist())

    # Remove duplicates and the given movie itself
    similar_movies = list(set(similar_movies) - {movie_id})

    # Filter recommendations by genre
    recommendations_by_genre = recommendations_by_rating[recommendations_by_rating['item_id'].isin(similar_movies)]

    return recommendations_by_genre

# Example of getting recommendations for 'Star Wars (1977)'
# movie_id = 1 # Replace with the movie_id you want recommendations for
# recommendations = get_movie_recommendations_by_genre_and_rating(movie_id, cube)

# Print recommended movies
# print("Recommended movies for movie_id '{}'".format(movie_id))
# print(recommendations)
