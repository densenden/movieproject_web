import sqlite3
import random

# Verbindung zur Datenbank herstellen
conn = sqlite3.connect('data/senflix.sqlite')
cursor = conn.cursor()

# Alle Movie-IDs abrufen
cursor.execute("SELECT id FROM movies")
movie_ids = [row[0] for row in cursor.fetchall()]

# Alle Category-IDs abrufen
cursor.execute("SELECT id FROM categories")
category_ids = [row[0] for row in cursor.fetchall()]

# Für jeden Film 1-3 zufällige Kategorien zuweisen
for movie_id in movie_ids:
    # 1-3 zufällige Kategorien auswählen
    num_categories = random.randint(1, 3)
    selected_categories = random.sample(category_ids, num_categories)
    
    # Beziehungen in die Datenbank eintragen
    for category_id in selected_categories:
        cursor.execute(
            "INSERT OR IGNORE INTO movie_categories (movie_id, category_id) VALUES (?, ?)",
            (movie_id, category_id)
        )

# Änderungen speichern und Verbindung schließen
conn.commit()
conn.close()

print("Movie-Category Beziehungen erfolgreich erstellt!") 