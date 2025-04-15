from flask_sqlalchemy import SQLAlchemy
from .interface import DataManagerInterface

db = SQLAlchemy()

class Avatar(db.Model):
    """
    Represents user avatar images in the system.
    
    Attributes:
        id (int): Primary key
        name (str): Avatar name/identifier
        image (str): Image filename stored in static/avatars/
    """
    __tablename__ = 'avatars'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    image = db.Column(db.Text)

    @property
    def profile_image_url(self):
        """Returns the full path for the profile image"""
        return f"static/avatars/profile/{self.image}" if self.image else None

    @property
    def hero_image_url(self):
        """Returns the full path for the hero image"""
        return f"static/avatars/hero/{self.image}" if self.image else None

class User(db.Model):
    """
    Represents a user in the system.
    
    Attributes:
        id (int): Primary key
        name (str): User's name
        whatsapp_number (str): User's WhatsApp contact number
        description (str): User's profile description
        avatar_id (int): Foreign key to Avatar
        favorites (relationship): One-to-many relationship with UserFavorite
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    whatsapp_number = db.Column(db.String(20))
    description = db.Column(db.Text)
    avatar_id = db.Column(db.Integer, db.ForeignKey('avatars.id'))
    favorites = db.relationship('UserFavorite', backref='user', lazy=True)
    avatar = db.relationship('Avatar', backref='users')

class Movie(db.Model):
    """
    Represents a movie in the system.
    
    Attributes:
        id (int): Primary key
        name (str): Movie name
        platforms (relationship): Many-to-many relationship with StreamingPlatform
        categories (relationship): Many-to-many relationship with Category
    """
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    platforms = db.relationship('StreamingPlatform', secondary='movie_platforms', lazy='dynamic',
                              backref=db.backref('movies', lazy=True))
    categories = db.relationship('Category', secondary='movie_categories', lazy='dynamic',
                               backref=db.backref('movies', lazy=True))

class UserFavorite(db.Model):
    """
    Represents a user's favorite movie with additional metadata.
    
    Attributes:
        user_id (int): Foreign key to User
        movie_id (int): Foreign key to Movie
        watched (bool): Whether the user has watched the movie
        comment (str): User's comment about the movie
        rating (float): User's rating of the movie
        watchlist (bool): Whether the movie is on user's watchlist
    """
    __tablename__ = 'user_favorites'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key=True)
    watched = db.Column(db.Boolean, default=False)
    comment = db.Column(db.Text)
    rating = db.Column(db.Float)
    watchlist = db.Column(db.Boolean, default=False)
    movie = db.relationship('Movie', backref='favorites')

class StreamingPlatform(db.Model):
    """
    Represents a streaming platform where movies are available.
    
    Attributes:
        id (int): Primary key
        name (str): Name of the streaming platform
    """
    __tablename__ = 'streaming_platforms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class MoviePlatform(db.Model):
    """
    Junction table for many-to-many relationship between Movie and StreamingPlatform.
    
    Attributes:
        movie_id (int): Foreign key to Movie
        platform_id (int): Foreign key to StreamingPlatform
    """
    __tablename__ = 'movie_platforms'
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key=True)
    platform_id = db.Column(db.Integer, db.ForeignKey('streaming_platforms.id'), primary_key=True)

class Category(db.Model):
    """
    Represents a movie category/genre.
    
    Attributes:
        id (int): Primary key
        name (str): Name of the category
        img (str): Image filename in static/categories/
    """
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    img = db.Column(db.String(255))

    @property
    def img_url(self):
        """Returns the full path for the category image"""
        return f"static/categories/{self.img}" if self.img else None

class MovieCategory(db.Model):
    """
    Junction table for many-to-many relationship between Movie and Category.
    
    Attributes:
        movie_id (int): Foreign key to Movie
        category_id (int): Foreign key to Category
    """
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
        """
        Return all category names and images for a given movie.
        
        Returns:
            list: List of dictionaries containing category name and image URL
            [
                {
                    'name': category.name,
                    'img': category.img_url
                }
                for category in movie.categories
            ]
        """
        movie = Movie.query.get(movie_id)
        if not movie:
            return []
        return [
            {
                'name': category.name,
                'img': category.img_url
            }
            for category in movie.categories
        ]

    def add_user(self, name, whatsapp_number, description=None, avatar_id=None):
        """
        Create new user with optional description and avatar.
        
        Args:
            name (str): User's name
            whatsapp_number (str): User's WhatsApp number
            description (str, optional): User's profile description
            avatar_id (int, optional): ID of the avatar to associate with user
        
        Returns:
            int: ID of the newly created user
        """
        user = User(
            name=name,
            whatsapp_number=whatsapp_number,
            description=description,
            avatar_id=avatar_id
        )
        db.session.add(user)
        db.session.commit()
        return user.id

    def get_user_data(self, user_id):
        """
        Return complete user data including all favorites, comments and watch history.
        
        Returns:
            dict: User data with the following structure:
            {
                'id': user.id,
                'name': user.name,
                'whatsapp_number': user.whatsapp_number,
                'description': user.description,
                'avatar': {
                    'profile_image': user.avatar.profile_image_url if user.avatar else None,
                    'hero_image': user.avatar.hero_image_url if user.avatar else None
                },
                'favorites': [
                    {
                        'movie_id': fav.movie_id,
                        'title': fav.movie.name,
                        'watched': fav.watched,
                        'comment': fav.comment,
                        'rating': fav.rating,
                        'watchlist': fav.watchlist
                    }
                    for fav in user.favorites
                ]
            }
        """
        user = User.query.get(user_id)
        if not user:
            return None
            
        return {
            'id': user.id,
            'name': user.name,
            'whatsapp_number': user.whatsapp_number,
            'description': user.description,
            'avatar': {
                'profile_image': user.avatar.profile_image_url if user.avatar else None,
                'hero_image': user.avatar.hero_image_url if user.avatar else None
            },
            'favorites': [
                {
                    'movie_id': fav.movie_id,
                    'title': fav.movie.name,
                    'watched': fav.watched,
                    'comment': fav.comment,
                    'rating': fav.rating,
                    'watchlist': fav.watchlist
                }
                for fav in user.favorites
            ]
        }

    def get_movie_data(self, movie_id):
        """
        Return complete movie data including categories and platforms.
        
        Returns:
            dict: Movie data with the following structure:
            {
                'id': movie.id,
                'title': movie.name,
                'categories': [category.name for category in movie.categories],
                'platforms': [platform.name for platform in movie.platforms],
                'user_data': [
                    {
                        'user_id': fav.user_id,
                        'watched': fav.watched,
                        'comment': fav.comment,
                        'rating': fav.rating,
                        'watchlist': fav.watchlist
                    }
                    for fav in movie.favorites
                ]
            }
        """
        movie = Movie.query.get(movie_id)
        if not movie:
            return None
            
        return {
            'id': movie.id,
            'title': movie.name,
            'categories': [category.name for category in movie.categories],
            'platforms': [platform.name for platform in movie.platforms],
            'user_data': [
                {
                    'user_id': fav.user_id,
                    'watched': fav.watched,
                    'comment': fav.comment,
                    'rating': fav.rating,
                    'watchlist': fav.watchlist
                }
                for fav in movie.favorites
            ]
        }

    def get_movies_by_category(self, category_id):
        """
        Return all movies in a specific category.
        
        Args:
            category_id (int): ID of the category
            
        Returns:
            list: List of Movie objects in the specified category
        """
        return Movie.query.join(MovieCategory).filter(
            MovieCategory.category_id == category_id
        ).all()
