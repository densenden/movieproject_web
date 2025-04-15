from datamanager.omdb_manager import OMDBManager
from datamanager.db_manager import Movie, db
from app import app

def main():
    with app.app_context():
        # OMDB Manager initialisieren
        omdb_manager = OMDBManager()
        
        print("Teste OMDB API Integration...")
        
        # Hole die ersten 10 Filme aus der Datenbank
        movies = Movie.query.limit(10).all()
        
        if not movies:
            print("Keine Filme in der Datenbank gefunden!")
            return
            
        print(f"Gefunden: {len(movies)} Filme")
        
        # Für jeden Film in der Liste
        for movie in movies:
            try:
                print(f"\nVerarbeite: {movie.name}")
                
                # OMDB Daten abrufen und speichern
                result = omdb_manager.get_movie_data(movie.id, movie.name)
                
                if result.get('Response') == 'True':
                    print(f"✓ Erfolgreich gespeichert")
                    print(f"  - IMDB ID: {result.get('imdbID')}")
                    print(f"  - Rating: {result.get('imdbRating')}")
                    print(f"  - Genre: {result.get('Genre')}")
                else:
                    print(f"✗ Fehler: {result.get('Error')}")
                    
            except Exception as e:
                print(f"✗ Fehler bei {movie.name}: {str(e)}")
                
        print("\nTest abgeschlossen!")

if __name__ == "__main__":
    main() 