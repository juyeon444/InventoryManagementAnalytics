import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
}

class DatabaseConnection:
    """Singleton class for managing MySQL database connection."""
    _instance = None  

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = cls._create_connection()
        return cls._instance

    @staticmethod
    def _create_connection():
        """Create a new database connection."""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            if connection.is_connected():
                print("Connected to the database.")
                return connection
        except Error as e:
            print(f"Error: {e}")
            return None

    def get_db_connection(self):
        """Return an active database connection, reconnect if necessary."""
        if not self.connection or not self.connection.is_connected():
            print("Reconnecting to the database...")
            self.connection = self._create_connection()
        return self.connection

    def close_connection(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")
    
    def execute_query(self, query):
        """Execute SQL query and return results."""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Database error: {e}")
            return []


db = DatabaseConnection()
