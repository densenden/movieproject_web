
import sqlite3
from interface import DataManagerInterface

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_path="data/senflix.sqlite"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def get_all_users(self):
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()

    def get_user_by_id(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return self.cursor.fetchone()

    def get_user_favorites(self, user_id):
        self.cursor.execute("""
            SELECT m.*, uf.watched, uf.comment, uf.rating
            FROM user_favorites uf
            JOIN movies m ON uf.movie_id = m.id
            WHERE uf.user_id = ?
        """, (user_id,))
        return self.cursor.fetchall()

    def add_favorite(self, user_id, movie_id, watched=False, comment=None, rating=None):
        self.cursor.execute("""
            INSERT INTO user_favorites (user_id, movie_id, watched, comment, rating)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, movie_id, int(watched), comment, rating))
        self.conn.commit()

    def remove_favorite(self, user_id, movie_id):
        self.cursor.execute("""
            DELETE FROM user_favorites WHERE user_id = ? AND movie_id = ?
        """, (user_id, movie_id))
        self.conn.commit()

    def get_all_movies(self):
        self.cursor.execute("SELECT * FROM movies")
        return self.cursor.fetchall()

    def get_movie_platforms(self, movie_id):
        self.cursor.execute("""
            SELECT sp.name
            FROM movie_platforms mp
            JOIN streaming_platforms sp ON mp.platform_id = sp.id
            WHERE mp.movie_id = ?
        """, (movie_id,))
        return [row["name"] for row in self.cursor.fetchall()]

    def get_movie_categories(self, movie_id):
        self.cursor.execute("""
            SELECT c.name
            FROM movie_categories mc
            JOIN categories c ON mc.category_id = c.id
            WHERE mc.movie_id = ?
        """, (movie_id,))
        return [row["name"] for row in self.cursor.fetchall()]

    def add_user(self, name, whatsapp_number):
        self.cursor.execute("""
            INSERT INTO users (name, whatsapp_number) VALUES (?, ?)
        """, (name, whatsapp_number))
        self.conn.commit()
        return self.cursor.lastrowid
