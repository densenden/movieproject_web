from flask import Flask, render_template
from datamanager import *
import os
import sys

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'senflix.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DataManager
data_manager = SQLiteDataManager(app)

@app.route('/')
def index():
    # Debug database connection
    print("Database path:", db_path, file=sys.stderr)
    print("Database exists:", os.path.exists(db_path), file=sys.stderr)
    
    # Get all categories with their movies from DataManager
    try:
        categories = data_manager.get_all_categories_with_movies()
        print("Successfully loaded categories", file=sys.stderr)
        
        # Debug output
        print("Loaded categories:", len(categories), file=sys.stderr)
        for category in categories:
            print(f"Category: {category['name']}, Movies: {len(category['movies'])}", file=sys.stderr)
            for movie in category['movies']:
                print(f"  - Movie: {movie['title']}", file=sys.stderr)
    except Exception as e:
        print(f"Error loading categories: {str(e)}", file=sys.stderr)
        categories = []
    
    return render_template('index.html', categories=categories)

if __name__ == '__main__':
    app.run(debug=True) 