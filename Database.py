import sqlite3
import cv2
import numpy as np

class DatabaseHandler:
    def __init__(self, database_path='../TouchPoint-Detection-Advancements-in-Projector-Camera-HCI/gestify.db'):
        self.database_path = database_path

    def create_database(self):
        try:
            self.connection = sqlite3.connect(self.database_path)
            cursor = self.connection.cursor()

            # Create a table for face encodings with an 'id', 'username', 'password', and 'encoding' column
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    face_img BLOB NOT NULL
                )
            ''')

            self.connection.commit()
        except Exception as e:
            print(f"Error creating database: {e}")

    def insert_face_image(self, username, password, face_img):
        try:
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()

            # Convert face image to bytes for storage in database
            _, encoding_bytes = cv2.imencode('.png', face_img)  # Use .png for generic image encoding

            # Insert face image into the database
            cursor.execute('''
                INSERT INTO faces (username, password, face_img) VALUES (?, ?, ?)
            ''', (username, password, encoding_bytes))

            connection.commit()

            # Return the ID of the inserted row
            face_id = cursor.lastrowid

            cursor.close()
            connection.close()

            return face_id
        except Exception as e:
            print(f"Error inserting face image: {e}")
            return None

    def load_face_images(self):
        try:
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()

            # Execute query to retrieve face images
            cursor.execute('SELECT id, username, face_img FROM faces')
            rows = cursor.fetchall()

            # Process and return the retrieved data
            face_images = []
            for row in rows:
                face_id = row[0]
                username = row[1]
                encoding_bytes = row[2]

                # Convert encoding bytes back to numpy array (image)
                nparr = np.frombuffer(encoding_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                # Append to the list of face images
                face_images.append((face_id, username, img))

            cursor.close()
            connection.close()

            return face_images
        except Exception as e:
            print(f"Error loading face images from database: {e}")
            return []

    def check_user(self, username, password):
        try:
            connection = sqlite3.connect(self.database_path)
            cursor = connection.cursor()

            # Query to check if user exists with given username and password
            cursor.execute('SELECT * FROM faces WHERE username=? AND password=?', (username, password))
            user_data = cursor.fetchone()

            cursor.close()
            connection.close()

            return user_data  # Returns user data if found (or None if not found)
        except Exception as e:
            print(f"Error checking user: {e}")
            return None