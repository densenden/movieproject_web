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
        """
        Return all category names and images for a given movie.
        
        Returns:
            list: List of dictionaries containing category name and image URL
            [
                {
                    'name': category.name,
                    'img': category.img
                }
                for category in movie.categories
            ]
        """
        pass

    @abstractmethod
    def add_user(self, name, whatsapp_number, description=None, avatar_url=None):
        """Create new user with optional description and avatar URL"""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id):
        """Return user info for given ID"""
        pass

    @abstractmethod
    def get_movie_data(self, movie_id):
        """Return complete movie data including categories and platforms"""
        pass

    @abstractmethod
    def get_user_data(self, user_id):
        """Return complete user data including all favorites, comments and watch history"""
        pass

    @abstractmethod
    def get_movies_by_category(self, category_id):
        """Return all movies in a specific category"""
        pass

    @abstractmethod
    def get_all_categories_with_movies(self):
        """
        Get all categories with their associated movies.
        
        Returns:
            list: List of dictionaries containing category data and movies
            [
                {
                    'id': category.id,
                    'name': category.name,
                    'hero_image': category.img_url,
                    'movies': [
                        {
                            'id': movie.id,
                            'title': movie.name,
                            'description': f"Movie in category {category.name}"
                        }
                        for movie in category.movies
                    ]
                }
                for category in categories
            ]
        """
        pass