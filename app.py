from flask import Flask, request, render_template, jsonify
import requests
import pandas as pd

import pandas as pd
import plotly.express as px

from agent_rating_genre import get_movie_recommendations_by_genre_and_rating, cube, merged_data, movie_id_title
from agent_genre import get_genre_recommendations, cube2

app = Flask(__name__)


# Define a route for the home page
@app.route('/')
def index():
    return render_template('index.html')


# Define a route for processing the user's movie recommendation request
@app.route('/recommend', methods=['POST'])
def recommend():
    # Get the user input from the form
    global movie_name
    movie_name = request.form.get('movie_name')

    # Find the movie_id based on the movie name
    try:
        movie_id = movie_id_title[movie_id_title['title'] == movie_name]['item_id'].values[0]
    except IndexError:
        return "Movie not found."

    # Get movie recommendations
    recommendations = get_movie_recommendations_by_genre_and_rating(movie_id, cube)

    # Prepare the recommendations for rendering
    recommendation_list = []

    # Inside your loop for recommendations
    for i, (_, similarity) in enumerate(recommendations.iterrows()):
        if i >= 10:  # Show the top 10 recommendations
            break
        movie_id = similarity['item_id']
        movie_title_with_year = movie_id_title[movie_id_title['item_id'] == movie_id]['title'].values[0]

        # Extract the movie title without the year (assuming the year is enclosed in parentheses)
        movie_title = movie_title_with_year.rsplit('(', 1)[0].strip()

        # Fetch the movie poster image URL using TMDb API
        api_key = 'c5747883c9921e7740e1d63614945b88'  # Replace with your TMDb API key
        tmdb_movie_name = movie_title  # Use the modified movie title for the TMDb API request
        tmdb_movie_name = tmdb_movie_name.replace(" ", "+")  # Replace spaces with '+' in the movie title

        # Make the API request to fetch movie poster
        tmdb_url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={tmdb_movie_name}'
        tmdb_response = requests.get(tmdb_url)

        if tmdb_response.status_code == 200:
            tmdb_data = tmdb_response.json()

            # Check if there are any results in the response
            if 'results' in tmdb_data and tmdb_data['results']:
                # Extract poster path from the first result
                poster_path = tmdb_data['results'][0]['poster_path']

                # Construct the full image URL
                base_url = 'https://image.tmdb.org/t/p/w500/'  # You can change the image size here
                image_url = base_url + poster_path

                recommendation_list.append((i + 1, movie_title_with_year, image_url))
            else:
                recommendation_list.append(
                    (i + 1, movie_title_with_year, 'No image available'))
        else:
            recommendation_list.append((i + 1, movie_title_with_year, 'Image request failed'))
    return render_template('recommendations.html', movie_name=movie_name, movie_id=movie_id,
                           recommendations=recommendation_list)


# Load movie titles from your CSV file
df = pd.read_csv('Movie_Id_Titles')
movie_names = df['title'].tolist()


@app.route('/process_response/<int:movie_id>/<int:response>', methods=['GET'])
def process_response(movie_id, response):
    if response == 1:
        return render_template('index.html')
    elif response == 0:
        print("zzzzzzzzzzzzzz")
        print(movie_id)
        recommendations = get_genre_recommendations(movie_id, cube2)

        recommendation_list = []

        for i, movie_id in enumerate(recommendations['item_id']):
            if i >= 10:  # Show the top 10 recommendations
                break
            movie_title_with_year = movie_id_title[movie_id_title['item_id'] == movie_id]['title'].values[0]
            movie_title = movie_title_with_year.rsplit('(', 1)[0].strip()
            api_key = 'c5747883c9921e7740e1d63614945b88'
            tmdb_movie_name = movie_title.replace(" ", "+")

            tmdb_url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={tmdb_movie_name}'
            tmdb_response = requests.get(tmdb_url)

            if tmdb_response.status_code == 200:
                tmdb_data = tmdb_response.json()

                if 'results' in tmdb_data and tmdb_data['results']:
                    poster_path = tmdb_data['results'][0]['poster_path']
                    base_url = 'https://image.tmdb.org/t/p/w500/'
                    image_url = base_url + poster_path

                    recommendation_list.append((i + 1, movie_title_with_year, image_url))
                else:
                    recommendation_list.append((i + 1, movie_title_with_year, 'No image available'))
            else:
                recommendation_list.append((i + 1, movie_title_with_year, 'Image request failed'))

        return render_template('recommendations.html', movie_name=movie_name, movie_id=movie_id,
                               recommendations=recommendation_list)


@app.route('/suggestions', methods=['GET'])
def movie_name_suggestions():
    query = request.args.get('query', '').lower()

    # Filter movie titles based on the query
    suggestions = [movie for movie in movie_names if query in movie.lower()]

    return jsonify(suggestions)


@app.route('/charts')
def show_charts():
    # Load your CSV data
    df = pd.read_csv('Movie_Id_Titles')

    # Split and count the genres
    genre_counts = df['genres'].str.split('|').explode().value_counts().reset_index()
    genre_counts.columns = ['Genre', 'Count']

    # Create a bar chart using Plotly Express
    fig = px.bar(genre_counts, x='Genre', y='Count', title='Number of Movies per Genre')

    # Convert the Plotly figure to JSON for rendering in the HTML template
    chart_json = fig.to_json()

    return render_template('charts.html', chart_json=chart_json)


if __name__ == '__main__':
    app.run(debug=True)
