
from db_manager import SQLiteDataManager

def print_user_favorites(dm, user_id):
    user = dm.get_user_by_id(user_id)
    print(f"User: {user['name']} (ID: {user_id})\nFavorites:")
    favorites = dm.get_user_favorites(user_id)
    for f in favorites:
        print(f"  - {f['name']} ({f['year']}), Rating: {f['rating']}, Comment: {f['comment']}")

def print_all_users(dm):
    users = dm.get_all_users()
    print("\nAll Users:")
    for u in users:
        print(f"  - {u['id']}: {u['name']} ({u['whatsapp_number']})")

def main():
    dm = SQLiteDataManager()

    print_all_users(dm)
    print_user_favorites(dm, 1)

    print("\nAvailable platforms for Movie 1:")
    print(dm.get_movie_platforms(1))

    print("\nCategories for Movie 1:")
    print(dm.get_movie_categories(1))

if __name__ == "__main__":
    main()
