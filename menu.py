from db_connect import execute_query, connect_to_db_direct
import pypyodbc
from typing import Optional, List, Tuple
import inspect

def main() -> None:
    print("🚀 Démarrage de l'application")
    
    # Demande du chemin de la base de données
    db_path: str = input("Chemin de la base de données: ")
    
    # Connexion à la BDD
    conn: Optional[pypyodbc.Connection] = connect_to_db_direct()
    if not conn:
        return
    
    try:
        while True:
            # Menu simple
            print("\n--- Menu ---")
            print("1. Lister les tables")
            print("2. Exécuter une requête SQL")
            print("3. Quitter")
            choice: str = input("Choix: ")
            
            if choice == "1":
                # Liste des tables avec les fonctions de la librairie
                cursor: Optional[pypyodbc.Cursor] = conn.cursor()
                for table in cursor.tables():
                    print(table[2])
                    
                
            elif choice == "2":
                query: str = input("Entrez votre requête SQL: ")
                cursor: Optional[pypyodbc.Cursor] = execute_query(conn, query)
                if cursor:
                    rows: List[Tuple] = cursor.fetchall()
                    if rows:
                        for row in rows:
                            print(row)
                    else:
                        print("Aucun résultat ou requête exécutée sans retour de données")
            
            elif choice == "3":
                break
            
            else:
                print("Option invalide")
    
    finally:
        conn.close()
        print("Connexion fermée ✅")

if __name__ == "__main__":
    main()
