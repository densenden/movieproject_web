import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json
from datamanager.omdb_manager import OMDBManager, MovieOMDB
from datamanager.db_manager import Movie
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TestOMDBManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a test database
        cls.test_db_path = Path(__file__).parent / "test_senflix.sqlite"
        cls.engine = create_engine(f'sqlite:///{cls.test_db_path}')
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)
        
    @classmethod
    def tearDownClass(cls):
        # Clean up test database
        cls.test_db_path.unlink(missing_ok=True)
        
    def setUp(self):
        # Create a new OMDBManager instance for each test
        self.omdb_manager = OMDBManager()
        # Override the database path for testing
        self.omdb_manager.db_path = self.test_db_path
        self.omdb_manager.engine = self.engine
        self.omdb_manager.Session = self.Session
        
        # Create test movie entries
        with self.Session() as session:
            # Create movies for testing
            for i in range(1, 4):
                movie = Movie(
                    id=i,
                    title=f"Test Movie {i}",
                    year=2020 + i,
                    description=f"Description for movie {i}",
                    duration=120,
                    rating=7.5,
                    poster_path=f"/path/to/poster{i}.jpg",
                    trailer_url=f"https://youtube.com/watch?v=trailer{i}",
                    release_date=f"2020-{i:02d}-01"
                )
                session.add(movie)
            session.commit()
        
    def tearDown(self):
        # Clear the database after each test
        with self.Session() as session:
            session.query(MovieOMDB).delete()
            session.query(Movie).delete()
            session.commit()
            
    @patch('requests.get')
    def test_get_movie_data_new(self, mock_get):
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'Title': 'Test Movie',
            'Year': '2023',
            'imdbID': 'tt1234567',
            'Poster': 'http://example.com/poster.jpg',
            'Response': 'True'
        }
        mock_get.return_value = mock_response
        
        # Test getting new movie data
        result = self.omdb_manager.get_movie_data(1, 'Test Movie', '2023')
        
        # Verify API was called
        mock_get.assert_called_once()
        
        # Verify result
        self.assertEqual(result['Title'], 'Test Movie')
        self.assertEqual(result['Year'], '2023')
        
        # Verify data was saved to database
        with self.Session() as session:
            movie = session.query(MovieOMDB).filter_by(id=1).first()
            self.assertIsNotNone(movie)
            self.assertEqual(movie.title, 'Test Movie')
            
    def test_get_movie_data_existing(self):
        # First save some test data
        test_data = {
            'Title': 'Existing Movie',
            'Year': '2022',
            'imdbID': 'tt7654321',
            'Response': 'True'
        }
        with self.Session() as session:
            movie = MovieOMDB(
                id=2,
                imdb_id=test_data['imdbID'],
                title=test_data['Title'],
                year=test_data['Year'],
                raw_data=test_data
            )
            session.add(movie)
            session.commit()
            
        # Test getting existing movie data
        result = self.omdb_manager.get_movie_data(2, 'Existing Movie')
        
        # Verify result
        self.assertEqual(result['Title'], 'Existing Movie')
        self.assertEqual(result['Year'], '2022')
        
    @patch('requests.get')
    def test_get_movie_data_not_found(self, mock_get):
        # Mock API response for movie not found
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'Response': 'False',
            'Error': 'Movie not found'
        }
        mock_get.return_value = mock_response
        
        # Test getting non-existent movie
        result = self.omdb_manager.get_movie_data(3, 'Non Existent Movie')
        
        # Verify result
        self.assertEqual(result['Response'], 'False')
        self.assertEqual(result['Error'], 'Movie not found on OMDb')
        
    @patch('requests.get')
    def test_download_poster(self, mock_get):
        # Mock successful poster download
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'test image data'
        mock_get.return_value = mock_response
        
        # Test poster download
        poster_path = self.omdb_manager._download_poster('tt1234567', 'http://example.com/poster.jpg')
        
        # Verify poster was downloaded
        self.assertIsNotNone(poster_path)
        self.assertTrue(poster_path.exists())
        
        # Clean up
        poster_path.unlink()
        
    @patch('requests.get')
    def test_download_poster_failed(self, mock_get):
        # Mock failed poster download
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Test failed poster download
        poster_path = self.omdb_manager._download_poster('tt1234567', 'http://example.com/poster.jpg')
        
        # Verify no poster was downloaded
        self.assertIsNone(poster_path)

if __name__ == '__main__':
    unittest.main() 