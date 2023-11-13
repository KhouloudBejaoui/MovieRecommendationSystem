import pandas as pd
from sqlalchemy import create_engine
from sklearn.metrics.pairwise import cosine_similarity

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
# Vous pouvez maintenant utiliser votre base de données pour l'analyse OLAP
# Define dimensions and measures
dimensions = ['user_id', 'item_id']
measures = ['rating']

# Create a multi-dimensional DataFrame (OLAP cube)
cube = merged_data.groupby(dimensions)[measures].sum()


# print(cube)

# Define a function to get movie recommendations for a user
def get_movie_recommendations(movie_id, cube):
    # Extract ratings for the given movie
    movie_ratings = cube.loc[(slice(None), movie_id), 'rating'].reset_index(level=1)

    # Pivot the table to get user ratings for all movies
    moviemat = cube.pivot_table(index='user_id', columns='item_id', values='rating')

    # Calculate the cosine similarity between the given movie and all other movies
    similar_movies = cosine_similarity(moviemat.T.fillna(0))

    # Get the index of the given movie
    movie_idx = movie_ratings.index.values[0]

    # Get the similarity scores for all movies
    movie_similarities = similar_movies[movie_idx]

    # Create a DataFrame of similar movies
    similar_movies_df = pd.DataFrame({'item_id': moviemat.columns, 'similarity': movie_similarities})

    # Sort the movies by similarity
    similar_movies_df = similar_movies_df.sort_values(by='similarity', ascending=False)

    # Filter out the movie itself
    similar_movies_df = similar_movies_df[similar_movies_df['item_id'] != movie_id]

    return similar_movies_df

# # Example of getting recommendations for 'Star Wars (1977)'
# movie_id = 50  # Replace with the movie_id you want recommendations for
# recommendations = get_movie_recommendations(movie_id, cube)

# # Print recommended movies
# print("Recommended movies for movie_id '{}'".format(movie_id))
# print(recommendations.head(10))
