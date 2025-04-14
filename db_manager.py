from flask_sqlalchemy import SQLAlchemy
from interface import DataManagerInterface

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    whatsapp_number = db.Column(db.String(20))
    favorites = db.relationship('UserFavorite', backref='user', lazy=True)

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    platforms = db.relationship('StreamingPlatform', secondary='movie_platforms', lazy='dynamic',
                              backref=db.backref('movies', lazy=True))
    categories = db.relationship('Category', secondary='movie_categories', lazy='dynamic',
                               backref=db.backref('movies', lazy=True))

class UserFavorite(db.Model):
    __tablename__ = 'user_favorites'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key=True)
    watched = db.Column(db.Boolean, default=False)
    comment = db.Column(db.Text)
    rating = db.Column(db.Float)
    movie = db.relationship('Movie', backref='favorites')

class StreamingPlatform(db.Model):
    __tablename__ = 'streaming_platforms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class MoviePlatform(db.Model):
    __tablename__ = 'movie_platforms'
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key=True)
    platform_id = db.Column(db.Integer, db.ForeignKey('streaming_platforms.id'), primary_key=True)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class MovieCategory(db.Model):
    __tablename__ = 'movie_categories'
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), primary_key=True)

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app=None):
        if app:
            db.init_app(app)
            with app.app_context():
                db.create_all()

    def get_all_users(self):
        return User.query.all()

    def get_user_by_id(self, user_id):
        return User.query.get(user_id)

    def get_user_favorites(self, user_id):
        return UserFavorite.query.filter_by(user_id=user_id).all()

    def add_favorite(self, user_id, movie_id, watched=False, comment=None, rating=None):
        favorite = UserFavorite(
            user_id=user_id,
            movie_id=movie_id,
            watched=watched,
            comment=comment,
            rating=rating
        )
        db.session.add(favorite)
        db.session.commit()

    def remove_favorite(self, user_id, movie_id):
        UserFavorite.query.filter_by(user_id=user_id, movie_id=movie_id).delete()
        db.session.commit()

    def get_all_movies(self):
        return Movie.query.all()

    def get_movie_platforms(self, movie_id):
        movie = Movie.query.get(movie_id)
        return [platform.name for platform in movie.platforms]

    def get_movie_categories(self, movie_id):
        movie = Movie.query.get(movie_id)
        return [category.name for category in movie.categories]

    def add_user(self, name, whatsapp_number):
        user = User(name=name, whatsapp_number=whatsapp_number)
        db.session.add(user)
        db.session.commit()
        return user.id

    def get_user_movies(self, user_id):
        return Movie.query.join(UserFavorite).filter(UserFavorite.user_id == user_id).all()
