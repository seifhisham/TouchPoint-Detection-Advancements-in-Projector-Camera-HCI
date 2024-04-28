import sqlite3

class DatabaseHandler:
    def __init__(self, database_path='../TouchPoint-Detection-Advancements-in-Projector-Camera-HCI/gestify.db'):
        self.database_path = database_path

    def create_users_table(self):
        try:
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()

            # Create a table for users with columns for username, password, and gesture commands
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    gesture1 TEXT DEFAULT NULL,
                    gesture2 TEXT DEFAULT NULL,
                    gesture3 TEXT DEFAULT NULL
                )
            ''')

            connection.commit()
            connection.close()
        except Exception as e:
            print(f"Error creating users table: {e}")

    def add_user(self, username, password):
        try:
            # Check if users table exists, create if not
            self.create_users_table()

            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()

            # Insert a new user into the database
            cursor.execute('''
                INSERT INTO users (username, password)
                VALUES (?, ?)
            ''', (username, password))

            connection.commit()
            connection.close()
            return True  # Return True indicating user added successfully
        except sqlite3.IntegrityError:
            print(f"User '{username}' already exists.")
            return False  # Return False if user already exists
        except Exception as e:
            print(f"Error adding user: {e}")
            return False

    def update_gestures(self, username, gesture1=None, gesture2=None, gesture3=None):
        try:
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()

            # Update the gesture commands for the specified user
            cursor.execute('''
                UPDATE users
                SET gesture1 = ?,
                    gesture2 = ?,
                    gesture3 = ?
                WHERE username = ?
            ''', (gesture1, gesture2, gesture3, username))

            connection.commit()
            connection.close()
            print(f"Gesture commands updated for user '{username}'.")
        except Exception as e:
            print(f"Error updating gestures: {e}")

    def get_user(self, username):
        try:
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()

            # Retrieve user data by username
            cursor.execute('''
                SELECT * FROM users
                WHERE username = ?
            ''', (username,))

            user_data = cursor.fetchone()
            connection.close()
            return user_data  # Returns user data if found (or None if not found)
        except Exception as e:
            print(f"Error getting user data: {e}")
            return None

    def fetch_user_gestures(self, username):
        try:
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()

            # Retrieve user's gesture commands from the database
            cursor.execute('''
                SELECT gesture1, gesture2, gesture3 FROM users
                WHERE username = ?
            ''', (username,))

            user_data = cursor.fetchone()
            connection.close()
            return user_data  # Returns (gesture1, gesture2, gesture3) tuple if user found
        except Exception as e:
            print(f"Error fetching user data: {e}")
            return None