import os
import sys
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datamanager.db_manager import SQLiteDataManager, db
from datamanager.omdb_manager import OMDBManager

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'senflix.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)  # Für Flash-Nachrichten

# Initialize DataManager and OMDBManager
data_manager = SQLiteDataManager(app)
omdb_manager = OMDBManager(data_manager)

def init_db():
    """Initialize the database with the correct schema"""
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()
        print("Database tables recreated successfully", file=sys.stderr)

# Uncomment the following line to recreate the database
init_db()

# Template context processor for user lookup
@app.context_processor
def utility_processor():
    def get_user(user_id):
        return data_manager.get_user_by_id(user_id)
    return dict(get_user=get_user)

@app.route('/')
def index():
    # Debug database connection
    print("Database path:", db_path, file=sys.stderr)
    print("Database exists:", os.path.exists(db_path), file=sys.stderr)
    
    try:
        # Get all categories with their movies from DataManager
        categories = data_manager.get_all_categories_with_movies()
        print("Successfully loaded categories", file=sys.stderr)
        
        # Debug output
        print("Loaded categories:", len(categories), file=sys.stderr)
        
        # Process each category and its movies
        for category in categories:
            print(f"Category: {category['name']}, Movies: {len(category['movies'])}", file=sys.stderr)
            
            # Add category image URL
            if category.get('img'):
                category['img_url'] = url_for('static', filename=f"categories/{category['img']}")
            else:
                category['img_url'] = url_for('static', filename='categories/default.jpg')
            
            # Process each movie in the category
            for movie in category['movies']:
                print(f"  - Movie: {movie['title']}", file=sys.stderr)
                
                # Get complete movie data including platforms
                movie_data = data_manager.get_movie_data(movie['id'])
                if movie_data:
                    movie['platforms'] = movie_data['platforms']
                
                # Load OMDB data for each movie
                omdb_data = omdb_manager.get_omdb_data(movie['id'])
                if omdb_data:
                    print(f"  - OMDB data found for {movie['title']}", file=sys.stderr)
                    movie['omdb_data'] = omdb_data
                    
                    # Add poster URL if available
                    if omdb_data.get('poster'):
                        movie['poster_url'] = url_for('static', filename=f"movies/{omdb_data['poster']}")
                    else:
                        movie['poster_url'] = url_for('static', filename='movies/no-poster.jpg')
                else:
                    print(f"  - No OMDB data for {movie['title']}", file=sys.stderr)
                    movie['poster_url'] = url_for('static', filename='movies/no-poster.jpg')
                    movie['omdb_data'] = None
                    
    except Exception as e:
        print(f"Error loading categories: {str(e)}", file=sys.stderr)
        categories = []
    
    return render_template('index.html', categories=categories)

@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    movie_data = data_manager.get_movie_data(movie_id)
    if not movie_data:
        flash('Movie not found', 'error')
        return redirect(url_for('index'))
        
    omdb_data = omdb_manager.get_omdb_data(movie_id)
    if omdb_data:
        movie_data['omdb_data'] = omdb_data
        
    return render_template('movie_details.html', movie=movie_data)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('index'))
        
    try:
        # Search in movie titles
        movies = data_manager.get_all_movies()
        results = []
        
        for movie in movies:
            if query.lower() in movie.name.lower():
                movie_data = data_manager.get_movie_data(movie.id)
                if movie_data:
                    omdb_data = omdb_manager.get_omdb_data(movie.id)
                    if omdb_data:
                        movie_data['omdb_data'] = omdb_data
                    results.append(movie_data)
                    
        return render_template('search_results.html', query=query, results=results)
    except Exception as e:
        flash(f'Error searching movies: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/users')
def users():
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)

@app.route('/users/<int:user_id>')
def user_movies(user_id):
    user_data = data_manager.get_user_data(user_id)
    if not user_data:
        flash('User not found', 'error')
        return redirect(url_for('users'))
    return render_template('user_movies.html', user=user_data)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form.get('name')
        whatsapp_number = request.form.get('whatsapp_number')
        description = request.form.get('description')
        
        if not name or not whatsapp_number:
            flash('Name and WhatsApp number are required', 'error')
            return redirect(url_for('add_user'))
            
        try:
            user_id = data_manager.add_user(name, whatsapp_number, description)
            flash('User successfully added', 'success')
            return redirect(url_for('user_movies', user_id=user_id))
        except Exception as e:
            flash(f'Error adding user: {str(e)}', 'error')
            return redirect(url_for('add_user'))
            
    return render_template('add_user.html')

@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == 'POST':
        movie_id = request.form.get('movie_id')
        watched = request.form.get('watched') == 'on'
        comment = request.form.get('comment')
        rating = request.form.get('rating')
        
        if not movie_id:
            flash('Please select a movie', 'error')
            return redirect(url_for('add_movie', user_id=user_id))
            
        try:
            data_manager.add_favorite(user_id, int(movie_id), watched, comment, float(rating) if rating else None)
            flash('Movie successfully added to favorites', 'success')
            return redirect(url_for('user_movies', user_id=user_id))
        except Exception as e:
            flash(f'Error adding movie: {str(e)}', 'error')
            return redirect(url_for('add_movie', user_id=user_id))
            
    movies = data_manager.get_all_movies()
    return render_template('add_movie.html', user_id=user_id, movies=movies)

@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    if request.method == 'POST':
        watched = request.form.get('watched') == 'on'
        comment = request.form.get('comment')
        rating = request.form.get('rating')
        
        try:
            data_manager.remove_favorite(user_id, movie_id)
            data_manager.add_favorite(user_id, movie_id, watched, comment, float(rating) if rating else None)
            flash('Movie successfully updated', 'success')
            return redirect(url_for('user_movies', user_id=user_id))
        except Exception as e:
            flash(f'Error updating movie: {str(e)}', 'error')
            return redirect(url_for('update_movie', user_id=user_id, movie_id=movie_id))
            
    user_data = data_manager.get_user_data(user_id)
    if not user_data:
        flash('User not found', 'error')
        return redirect(url_for('users'))
        
    movie_data = None
    for favorite in user_data['favorites']:
        if favorite['movie_id'] == movie_id:
            movie_data = favorite
            break
            
    if not movie_data:
        flash('Movie not found in favorites', 'error')
        return redirect(url_for('user_movies', user_id=user_id))
        
    return render_template('update_movie.html', user_id=user_id, movie=movie_data)

@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    try:
        data_manager.remove_favorite(user_id, movie_id)
        flash('Movie successfully removed from favorites', 'success')
    except Exception as e:
        flash(f'Error removing movie: {str(e)}', 'error')
    return redirect(url_for('user_movies', user_id=user_id))

if __name__ == '__main__':
    app.run(debug=True) 