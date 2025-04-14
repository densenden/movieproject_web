from flask import Flask
import os
from db_manager import SQLiteDataManager, db

def print_user_favorites(dm, user_id):
    user = dm.get_user_by_id(user_id)
    if user:
        print(f"User: {user.name} (ID: {user_id})\nFavorites:")
        favorites = dm.get_user_favorites(user_id)
        for f in favorites:
            print(f"  - {f.movie.title}, Rating: {f.rating}, Comment: {f.comment}")
    else:
        print(f"Kein Benutzer mit ID {user_id} gefunden.")

def print_all_users(dm):
    users = dm.get_all_users()
    print("\nAlle Benutzer:")
    for u in users:
        print(f"  - {u.id}: {u.name} ({u.whatsapp_number})")

def main():
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'data', 'senflix.sqlite')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    dm = SQLiteDataManager(app)

    with app.app_context():
        print_all_users(dm)
        print_user_favorites(dm, 1)

        print("\nVerfügbare Plattformen für Film 1:")
        print(dm.get_movie_platforms(1))

        print("\nKategorien für Film 1:")
        print(dm.get_movie_categories(1))

if __name__ == "__main__":
    main()
