import os
import sys
from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datamanager.db_manager import SQLiteDataManager
from datamanager.omdb_manager import OMDBManager

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'senflix.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DataManager and OMDBManager
data_manager = SQLiteDataManager(app)
omdb_manager = OMDBManager(data_manager)

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

if __name__ == '__main__':
    app.run(debug=True) 