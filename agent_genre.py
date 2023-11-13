import pandas as pd
from sqlalchemy import create_engine
from sklearn.metrics.pairwise import cosine_similarity
# Etape 1: Extraction
# Charger les fichiers CSV
column_names = ['user_id', 'item_id', 'rating', 'timestamp']
u_data = pd.read_csv('u.data', sep='\t', names=column_names)

movie_id_title = pd.read_csv("Movie_Id_Titles")
# Vérifier les types de données
print(u_data['item_id'].dtype)
print(movie_id_title['item_id'].dtype)

# Si les types ne correspondent pas, convertir l'un d'entre eux
# Par exemple, si l'un d'entre eux est de type str et l'autre est int, vous pouvez les convertir en int
# Exemple : 
u_data['item_id'] = u_data['item_id'].astype(int)

# Etape 2: Transformation
# Fusionner les données pour obtenir le titre des films
merged_data = pd.merge(u_data, movie_id_title, on='item_id')

# Filtrer les films sans genre
merged_data = merged_data[merged_data['genres'] != '0']

# Etape 3: Chargement
# Charger les données dans une base de données (SQLite par exemple)
engine = create_engine('sqlite:///movie.db')

# Charger les données transformées dans la base de données
merged_data.to_sql('movie_ratings', engine, if_exists='replace', index=False)

# Define dimensions and measures
dimensions = ['item_id', 'genres']  # Include 'user_id' in dimensions if needed

# Create a multi-dimensional DataFrame (OLAP cube)
cube2 = merged_data.groupby(dimensions).agg({'item_id': 'first', 'genres': 'first'})


# Define a function to get genre-based movie recommendations
def get_genre_recommendations(movie_id, cube2):
    # Extract genres for the given movie from the DataFrame 'cube'
    movie_genres = cube2[cube2['item_id'] == movie_id]['genres'].values
    if len(movie_genres) == 0:
        return []  # Movie has no genre information, return an empty list

    movie_genres = movie_genres[0].split('|')

    # Find movies with similar genres
    similar_movies = []

    for genre in movie_genres:
        cube_filtered = cube2[cube2['genres'].str.contains(genre)]
        similar_movies.extend(cube_filtered['item_id'].tolist())
    
    # Remove duplicates and the given movie itself
    similar_movies = list(set(similar_movies) - {movie_id})
    # Create a new DataFrame with the similar movie IDs
    similar_movies_df = cube2[cube2['item_id'].isin(similar_movies)]
   
    return similar_movies_df 


