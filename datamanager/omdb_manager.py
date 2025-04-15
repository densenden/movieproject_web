import os
import json
import requests
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .db_manager import db, Movie

class MovieOMDB(db.Model):
    """
    Represents OMDB data for a movie.
    
    Attributes:
        id (int): Primary key and foreign key to movies table
        imdb_id (str): IMDB ID of the movie
        title (str): Movie title
        year (str): Release year
        rated (str): Rating (PG, R, etc.)
        released (str): Release date
        runtime (str): Movie duration
        genre (str): Movie genres
        director (str): Director(s)
        writer (str): Writer(s)
        actors (str): Main actors
        plot (str): Movie plot summary
        language (str): Languages
        country (str): Countries of production
        awards (str): Awards won/nominated
        poster_path (str): Local path to poster image
        ratings (JSON): Array of ratings from different sources
        metascore (str): Metacritic score
        imdb_rating (str): IMDB rating
        imdb_votes (str): Number of IMDB votes
        type (str): Type (movie, series, etc.)
        dvd (str): DVD release date
        box_office (str): Box office earnings
        production (str): Production company
        website (str): Official website
        raw_data (JSON): Complete raw data from API
    """
    __tablename__ = 'movies_omdb'
    
    id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key=True)
    imdb_id = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    year = db.Column(db.String(10))
    rated = db.Column(db.String(10))
    released = db.Column(db.String(50))
    runtime = db.Column(db.String(20))
    genre = db.Column(db.String(255))
    director = db.Column(db.String(255))
    writer = db.Column(db.String(255))
    actors = db.Column(db.String(255))
    plot = db.Column(db.Text)
    language = db.Column(db.String(255))
    country = db.Column(db.String(255))
    awards = db.Column(db.Text)
    poster_path = db.Column(db.String(255))
    ratings = db.Column(db.JSON)
    metascore = db.Column(db.String(10))
    imdb_rating = db.Column(db.String(10))
    imdb_votes = db.Column(db.String(20))
    type = db.Column(db.String(20))
    dvd = db.Column(db.String(50))
    box_office = db.Column(db.String(50))
    production = db.Column(db.String(255))
    website = db.Column(db.String(255))
    raw_data = db.Column(db.JSON)
    
    # Relationship to Movie model
    movie = db.relationship("Movie", back_populates="omdb_data")

class OMDBManager:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OMDB_API_KEY')
        self.base_url = "http://www.omdbapi.com/"
        # Use absolute path for cache directory
        self.project_root = Path(__file__).parent.parent
        self.cache_dir = self.project_root / "data" / "movies"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_poster_path(self, movie_id: str) -> Path:
        """Returns the path for the poster image"""
        return self.cache_dir / f"{movie_id}-omdb-poster.jpg"
        
    def _is_in_db(self, movie_id: int) -> bool:
        """Checks if movie data is already in database"""
        return MovieOMDB.query.filter_by(id=movie_id).first() is not None
            
    def _save_to_db(self, movie_id: int, data: Dict) -> None:
        """Saves movie data to database"""
        # Download poster if available and get local path
        poster_path = None
        poster_url = data.get('Poster')
        if poster_url and poster_url != "N/A":
            poster_path = self._download_poster(data['imdbID'], poster_url)
            
        movie_omdb = MovieOMDB(
            id=movie_id,
            imdb_id=data.get('imdbID'),
            title=data.get('Title'),
            year=data.get('Year'),
            rated=data.get('Rated'),
            released=data.get('Released'),
            runtime=data.get('Runtime'),
            genre=data.get('Genre'),
            director=data.get('Director'),
            writer=data.get('Writer'),
            actors=data.get('Actors'),
            plot=data.get('Plot'),
            language=data.get('Language'),
            country=data.get('Country'),
            awards=data.get('Awards'),
            poster_path=str(poster_path) if poster_path else None,
            ratings=data.get('Ratings', []),
            metascore=data.get('Metascore'),
            imdb_rating=data.get('imdbRating'),
            imdb_votes=data.get('imdbVotes'),
            type=data.get('Type'),
            dvd=data.get('DVD'),
            box_office=data.get('BoxOffice'),
            production=data.get('Production'),
            website=data.get('Website'),
            raw_data=data
        )
        db.session.add(movie_omdb)
        db.session.commit()
            
    def _download_poster(self, imdb_id: str, poster_url: str) -> Optional[Path]:
        """Downloads and saves the poster image, returns the path if successful"""
        if poster_url == "N/A":
            return None
            
        poster_path = self._get_poster_path(imdb_id)
        response = requests.get(poster_url)
        if response.status_code == 200:
            with open(poster_path, 'wb') as f:
                f.write(response.content)
            return poster_path
        return None
                
    def _get_from_api(self, title: str, year: Optional[str] = None) -> Dict:
        """Fetches movie data from OMDb API"""
        params = {
            'apikey': self.api_key,
            't': title,
            'y': year,
            'plot': 'full'
        }
        response = requests.get(self.base_url, params=params)
        return response.json()
        
    def get_movie_data(self, movie_id: int, title: str, year: Optional[str] = None) -> Dict:
        """
        Main method to fetch movie data.
        First checks database, if not found fetches from API and stores in database.
        
        Args:
            movie_id (int): ID of the movie in the local database
            title (str): Movie title to search for
            year (Optional[str]): Release year of the movie
            
        Returns:
            Dict: Movie data including title, year, plot, etc.
        """
        # First check if already in database
        if self._is_in_db(movie_id):
            movie_omdb = MovieOMDB.query.filter_by(id=movie_id).first()
            if movie_omdb:
                return movie_omdb.raw_data
        
        # If not in database, fetch from API
        api_data = self._get_from_api(title, year)
        
        if api_data.get('Response') == 'False':
            return {
                'Response': 'False',
                'Error': 'Movie not found on OMDb',
                'Title': title,
                'Year': year
            }
            
        if not api_data.get('imdbID'):
            return {
                'Response': 'False',
                'Error': 'Invalid API response',
                'Title': title,
                'Year': year
            }
            
        # Save to database
        self._save_to_db(movie_id, api_data)
        return api_data 