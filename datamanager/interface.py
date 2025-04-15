from abc import ABC, abstractmethod

class DataManagerInterface(ABC):

    @abstractmethod
    def get_all_users(self):
        """Return list of all users"""
        pass

    @abstractmethod
    def get_user_favorites(self, user_id):
        """Return movies favorited by the user, with watched status, comment and rating"""
        pass

    @abstractmethod
    def add_favorite(self, user_id, movie_id, watched=False, comment=None, rating=None):
        """Add a movie to a user's favorites"""
        pass

    @abstractmethod
    def remove_favorite(self, user_id, movie_id):
        """Remove a movie from user's favorites"""
        pass

    @abstractmethod
    def get_all_movies(self):
        """Return all movies in the database"""
        pass

    @abstractmethod
    def get_movie_platforms(self, movie_id):
        """Return platforms where the movie is available"""
        pass

    @abstractmethod
    def get_movie_categories(self, movie_id):
        """Return all category names for a given movie"""
        pass

    @abstractmethod
    def add_user(self, name, whatsapp_number):
        """Create new user"""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id):
        """Return user info for given ID"""
        pass