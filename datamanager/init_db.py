from flask import Flask
import os
from . import db
from datamanager import (
    SQLiteDataManager, User, Movie, UserFavorite,
    StreamingPlatform, MoviePlatform, Category, MovieCategory
)

def init_db():
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'data', 'senflix.sqlite')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Datenbank wurde erfolgreich initialisiert!")
        print(f"Datenbank wurde erstellt unter: {db_path}")

if __name__ == "__main__":
    init_db() 