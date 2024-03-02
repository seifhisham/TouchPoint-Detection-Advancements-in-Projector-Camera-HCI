# database.py
import sqlite3

import cv2
import numpy as np

class DatabaseHandler:
    def __init__(self, database_path='./gestify.db'):
        self.database_path = database_path
        self.connection = None
        self.create_database()

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
                    encoding TEXT NOT NULL
                )
            ''')

            self.connection.commit()
        except Exception as e:
            print(f"Error creating database: {e}")

    def insert_face_encoding(self, username, password, encoding):
        try:
            cursor = self.connection.cursor()
            # Convert the encoding to bytes before inserting into the database
            encoding_bytes = sqlite3.Binary(encoding)
            cursor.execute('''
                        INSERT INTO faces (username, password, encoding) VALUES (?, ?, ?)
                    ''', (username, password, encoding_bytes))
            self.connection.commit()

            # Return the ID of the inserted row
            return cursor.lastrowid
        except Exception as e:
            print(f"Error inserting face encoding: {e}")
            return None

    def load_face_encodings(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT encoding FROM faces')
            rows = cursor.fetchall()

            # Ensure the encoding is retrieved as bytes
            return [np.frombuffer(row[0], dtype=np.uint8) for row in rows]
        except Exception as e:
            print(f"Error loading images from database: {e}")
            return []
