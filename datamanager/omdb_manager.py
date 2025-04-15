import os
import sys
import requests
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from .db_manager import db, MovieOMDB, Movie
import urllib.request
import ssl
from pathlib import Path

class OMDBManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.api_key = os.getenv('OMDB_API_KEY')
        self.api_url = "http://www.omdbapi.com/"
        # Create movies directory if it doesn't exist
        self.movies_dir = Path('static/movies')
        self.movies_dir.mkdir(parents=True, exist_ok=True)
        
        # Create SSL context that ignores certificate verification
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def save_poster(self, poster_url, movie_id, imdb_id):
        """Save movie poster to local storage"""
        print(f"\n=== Starting poster save process for movie {movie_id} ===", file=sys.stderr)
        print(f"Poster URL: {poster_url}", file=sys.stderr)
        
        if not poster_url or poster_url == 'N/A':
            print("No valid poster URL provided", file=sys.stderr)
            return None
            
        try:
            # Create filename using IMDB ID
            filename = f"{imdb_id}-omdb-poster.jpg"
            filepath = self.movies_dir / filename
            print(f"Target filepath: {filepath}", file=sys.stderr)
            
            # Check if directory exists
            if not self.movies_dir.exists():
                print(f"Creating directory: {self.movies_dir}", file=sys.stderr)
                self.movies_dir.mkdir(parents=True, exist_ok=True)
            
            # Download and save the image with SSL context
            print("Setting up SSL context and opener...", file=sys.stderr)
            opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=self.ssl_context))
            urllib.request.install_opener(opener)
            
            print("Starting download...", file=sys.stderr)
            urllib.request.urlretrieve(poster_url, filepath)
            print("Download completed successfully", file=sys.stderr)
            
            # Verify file was created
            if filepath.exists():
                print(f"File successfully saved at: {filepath}", file=sys.stderr)
                print(f"File size: {filepath.stat().st_size} bytes", file=sys.stderr)
            else:
                print("ERROR: File was not created", file=sys.stderr)
                return None
            
            # Return relative path for database storage
            return_value = filename
            print(f"Returning filename: {return_value}", file=sys.stderr)
            return return_value
            
        except Exception as e:
            print(f"Error saving poster: {str(e)}", file=sys.stderr)
            import traceback
            print("Traceback:", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            return None

    def fetch_omdb_data(self, title):
        """Fetch movie data from OMDB API"""
        if not self.api_key:
            print("OMDB API key not found", file=sys.stderr)
            return None
            
        params = {
            'apikey': self.api_key,
            't': title,
            'plot': 'full'
        }
        
        print(f"\n=== OMDB API Request ===", file=sys.stderr)
        print(f"Request URL: {self.api_url}", file=sys.stderr)
        print(f"Request Parameters: {params}", file=sys.stderr)
        
        try:
            response = requests.get(self.api_url, params=params, verify=False)
            print(f"Response Status Code: {response.status_code}", file=sys.stderr)
            print(f"Response Headers: {response.headers}", file=sys.stderr)
            
            response.raise_for_status()
            data = response.json()
            
            print(f"Response Data: {data}", file=sys.stderr)
            print(f"Response Status: {data.get('Response')}", file=sys.stderr)
            print(f"Error Message: {data.get('Error')}", file=sys.stderr)
            
            if data.get('Response') == 'False':
                print(f"API Error: {data.get('Error')}", file=sys.stderr)
                return None
                
            return data
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {str(e)}", file=sys.stderr)
            return None

    def get_omdb_data(self, movie_id):
        """Get OMDB data for a specific movie"""
        try:
            print(f"\n=== Getting OMDB data for movie {movie_id} ===", file=sys.stderr)
            
            # First check if we have the data in our database
            omdb_data = MovieOMDB.query.filter_by(id=movie_id).first()
            
            if omdb_data:
                print("Found existing data in database", file=sys.stderr)
                
                # Check if poster exists locally
                if omdb_data.imdb_id:
                    poster_path = self.movies_dir / f"{omdb_data.imdb_id}-omdb-poster.jpg"
                    if not poster_path.exists() and omdb_data.poster_img:
                        print("Poster not found locally, fetching from API...", file=sys.stderr)
                        movie = Movie.query.get(movie_id)
                        if movie:
                            api_data = self.fetch_omdb_data(movie.name)
                            if api_data and api_data.get('Response') != 'False' and api_data.get('Poster'):
                                print("Downloading poster from API...", file=sys.stderr)
                                poster_filename = self.save_poster(api_data.get('Poster'), movie_id, api_data.get('imdbID'))
                                if poster_filename:
                                    print("Updating poster filename in database...", file=sys.stderr)
                                    omdb_data.poster_img = poster_filename
                                    db.session.commit()
                
                return self._format_omdb_data(omdb_data)
            
            print("No data in database, fetching from API...", file=sys.stderr)
            # If not, fetch from OMDB API
            movie = Movie.query.get(movie_id)
            if not movie:
                print(f"Movie with ID {movie_id} not found", file=sys.stderr)
                return None
                
            api_data = self.fetch_omdb_data(movie.name)
            if api_data and api_data.get('Response') != 'False':
                print("Successfully fetched data from API", file=sys.stderr)
                # Convert API keys to match database column names
                db_data = {
                    'id': movie_id,
                    'imdb_id': api_data.get('imdbID'),
                    'title': api_data.get('Title'),
                    'year': api_data.get('Year'),
                    'rated': api_data.get('Rated'),
                    'released': api_data.get('Released'),
                    'runtime': api_data.get('Runtime'),
                    'genre': api_data.get('Genre'),
                    'director': api_data.get('Director'),
                    'writer': api_data.get('Writer'),
                    'actors': api_data.get('Actors'),
                    'plot': api_data.get('Plot'),
                    'language': api_data.get('Language'),
                    'country': api_data.get('Country'),
                    'awards': api_data.get('Awards'),
                    'poster_img': self.save_poster(api_data.get('Poster'), movie_id, api_data.get('imdbID')),
                    'imdb_rating': api_data.get('imdbRating'),
                    'rotten_tomatoes': api_data.get('Ratings', [{}])[0].get('Value') if api_data.get('Ratings') else None,
                    'metacritic': api_data.get('Metascore'),
                    'type': api_data.get('Type'),
                    'dvd': api_data.get('DVD'),
                    'box_office': api_data.get('BoxOffice'),
                    'production': api_data.get('Production'),
                    'website': api_data.get('Website')
                }
                # Save the data to our database
                if self.save_omdb_data(movie_id, db_data):
                    print("Successfully saved data to database", file=sys.stderr)
                    # After saving, get the data from database to ensure consistency
                    omdb_data = MovieOMDB.query.filter_by(id=movie_id).first()
                    if omdb_data:
                        return self._format_omdb_data(omdb_data)
                else:
                    print("Failed to save data to database", file=sys.stderr)
            else:
                print("Failed to fetch data from API", file=sys.stderr)
            return None
                
        except Exception as e:
            print(f"Error getting OMDB data: {str(e)}", file=sys.stderr)
            return None

    def _format_omdb_data(self, omdb_data):
        """Format OMDB data for API response"""
        return {
            'title': omdb_data.title,
            'year': omdb_data.year,
            'rated': omdb_data.rated,
            'released': omdb_data.released,
            'runtime': omdb_data.runtime,
            'genre': omdb_data.genre,
            'director': omdb_data.director,
            'writer': omdb_data.writer,
            'actors': omdb_data.actors,
            'plot': omdb_data.plot,
            'language': omdb_data.language,
            'country': omdb_data.country,
            'awards': omdb_data.awards,
            'poster': omdb_data.poster_img,
            'imdb_rating': omdb_data.imdb_rating,
            'rotten_tomatoes': omdb_data.rotten_tomatoes,
            'metacritic': omdb_data.metacritic,
            'type': omdb_data.type,
            'dvd': omdb_data.dvd,
            'box_office': omdb_data.box_office,
            'production': omdb_data.production,
            'website': omdb_data.website
        }

    def save_omdb_data(self, movie_id, omdb_data):
        """Save OMDB data for a movie"""
        try:
            # Check if movie exists
            movie = Movie.query.get(movie_id)
            if not movie:
                print(f"Movie with ID {movie_id} not found", file=sys.stderr)
                return False

            # Check if OMDB data already exists
            existing_data = MovieOMDB.query.filter_by(id=movie_id).first()
            
            if existing_data:
                # Update existing data
                for key, value in omdb_data.items():
                    if hasattr(existing_data, key):
                        # Special handling for poster_img
                        if key == 'poster_img' and value:
                            setattr(existing_data, key, value)
                        # For other fields, only update if value is not None
                        elif key != 'poster_img' and value is not None:
                            setattr(existing_data, key, value)
            else:
                # Create new OMDB data entry
                new_data = MovieOMDB(**omdb_data)
                db.session.add(new_data)

            db.session.commit()
            return True
        except Exception as e:
            print(f"Error saving OMDB data: {str(e)}", file=sys.stderr)
            db.session.rollback()
            return False 