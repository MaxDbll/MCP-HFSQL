import pypyodbc
from typing import Optional

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


def execute_query(conn: pypyodbc.Connection, query: str) -> Optional[pypyodbc.Cursor]:
    """Exécute une requête SQL"""
    try:
        cursor: pypyodbc.Cursor = conn.cursor()
        cursor.execute(query)
        return cursor
    except Exception as e:
        print(f"Erreur d'exécution: {e}")
        return None


def list_tables(conn: pypyodbc.Connection):
    """Liste les tables de la base de données"""
    try:
        cursor: pypyodbc.Cursor = conn.cursor()
        tables: list[str] = []
        for table in cursor.tables():
            tables.append(table[2])
        return tables
    except Exception as e:
        print(f"Erreur de liste des tables: {e}")
        return []
