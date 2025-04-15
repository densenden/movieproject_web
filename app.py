from flask import Flask, render_template
from datamanager import *
import os

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
    # Load all categories
    categories = []
    with app.app_context():
        for category in Category.query.all():
            # Load movies for each category
            movies = data_manager.get_movies_by_category(category.id)
            categories.append({
                'id': category.id,
                'name': category.name,
                'hero_image': category.img_url,
                'movies': [{
                    'id': movie.id,
                    'title': movie.name,
                    'description': f"Movie in category {category.name}"
                } for movie in movies]
            })
    
    return render_template('index.html', categories=categories)

if __name__ == '__main__':
    app.run(debug=True) 