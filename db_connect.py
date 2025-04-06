import pypyodbc
import json


class DatabaseConnection:
    def __init__(self, connection_string: str):
        self.connection_string: str = connection_string
        self.connection: pypyodbc.Connection
        self.cursor: pypyodbc.Cursor
     
    
    def __enter__(self):
        try:
            self.connection = pypyodbc.connect(self.connection_string)
            self.cursor = self.connection.cursor()
            return self
        except Exception as e:
            raise Exception(f"Erreur de connexion: {e}")

            
            
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
        return False
    
    

    # Error handler decorator
    @staticmethod
    def error_handler(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except pypyodbc.Error as e:
                return json.dumps({"error": f"Database error: {e}"})
            except Exception as e:
                return json.dumps({"error": f"An error occurred: {e}"})
        return wrapper