from flask import Flask
import os
from datamanager import (
    db, User, Movie, UserFavorite,
    StreamingPlatform, MoviePlatform, Category, MovieCategory
)

def seed_db():
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'data', 'senflix.sqlite')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Benutzer erstellen
        users = [
            User(name='Louise', whatsapp_number='+49 162 7933737'),
            User(name='Jörg', whatsapp_number='+49 176 24301783'),
            User(name='Chris', whatsapp_number='+49 1590 4891419'),
            User(name='Stefanos', whatsapp_number='+49 1517 2689928'),
            User(name='Spunky', whatsapp_number='+49 163 6654561'),
            User(name='Jon-Mark', whatsapp_number='+44 7710 047279'),
            User(name='Remo', whatsapp_number='+49 177 1637200'),
            User(name='Romano', whatsapp_number='+49 176 62048607'),
            User(name='Lisa', whatsapp_number='+49 176 30524940'),
            User(name='Stella', whatsapp_number='')
        ]
        db.session.add_all(users)
        
        # Filme erstellen
        movies = [
            Movie(title='The Matrix'),
            Movie(title='Inception'),
            Movie(title='The Dark Knight')
        ]
        db.session.add_all(movies)
        
        # Streaming-Plattformen erstellen
        platforms = [
            StreamingPlatform(name='Netflix'),
            StreamingPlatform(name='Amazon Prime'),
            StreamingPlatform(name='Disney+')
        ]
        db.session.add_all(platforms)
        
        # Kategorien erstellen
        categories = [
            Category(name='Action'),
            Category(name='Sci-Fi'),
            Category(name='Drama')
        ]
        db.session.add_all(categories)
        
        db.session.commit()
        
        # Verknüpfungen erstellen
        # Film-Plattform-Verknüpfungen
        movie_platforms = [
            MoviePlatform(movie_id=1, platform_id=1),  # Matrix auf Netflix
            MoviePlatform(movie_id=1, platform_id=2),  # Matrix auf Prime
            MoviePlatform(movie_id=2, platform_id=3),  # Inception auf Disney+
        ]
        db.session.add_all(movie_platforms)
        
        # Film-Kategorie-Verknüpfungen
        movie_categories = [
            MovieCategory(movie_id=1, category_id=1),  # Matrix - Action
            MovieCategory(movie_id=1, category_id=2),  # Matrix - Sci-Fi
            MovieCategory(movie_id=2, category_id=2),  # Inception - Sci-Fi
        ]
        db.session.add_all(movie_categories)
        
        # Benutzer-Favoriten
        favorites = [
            UserFavorite(user_id=1, movie_id=1, watched=True, rating=5, comment="Klassiker!"),
            UserFavorite(user_id=1, movie_id=2, watched=False, rating=None, comment="Will ich sehen"),
            UserFavorite(user_id=2, movie_id=1, watched=True, rating=4, comment="Gut")
        ]
        db.session.add_all(favorites)
        
        db.session.commit()
        print("Testdaten wurden erfolgreich eingefügt!")

if __name__ == "__main__":
    seed_db() 