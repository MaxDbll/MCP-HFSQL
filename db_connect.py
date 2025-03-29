import pypyodbc
from typing import Optional



class DatabaseConnection:
    def __init__(self, connection_string: str):
        self.connection_string: str = connection_string
        self.connection: pypyodbc.Connection | None = None
        self.cursor: pypyodbc.Cursor | None = None
     
    
    def __enter__(self):
        self.connection = None
        try:
            self.connection = pypyodbc.connect(self.connection_string)
            self.cursor = self.connection.cursor()
            print("Connexion réussie!")
            return self.connection
        except Exception as e:
            print(f"Erreur de connexion: {e}")

            
            
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
            print("Connexion fermée!")
        return False
    
    

def connect_to_db(dsn_name: str = "") -> Optional[pypyodbc.Connection]:
    """Connexion directe via pypyodbc à une base HFSQL (WinDev)"""
    try:
        connection_string: str = """
        DRIVER={HFSQL};Server Name=127.0.0.1;Server Port=4900;
Database=python_odbc;UID=admin;IntegrityCheck=1
        """
        conn: pypyodbc.Connection = pypyodbc.connect(connection_string)
        print("Connexion réussie!")
        return conn
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        return None
