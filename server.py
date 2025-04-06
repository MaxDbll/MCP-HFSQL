from typing import Any, Optional
from mcp.types import Resource
from mcp.server.fastmcp import FastMCP
from pydantic import AnyUrl
import json 
import os

from mcp.server.fastmcp.prompts import base
import pypyodbc

from db_connect import DatabaseConnection

mcp = FastMCP("HFSQL Assistant", dependencies=["pypyodbc"])

def connection_string():
    host: str = os.getenv("HFSQL_HOST", "localhost")
    port: str = os.getenv("HFSQL_PORT", "4900")
    database: str = os.getenv("HFSQL_DATABASE", "test_odbc")
    user: str = os.getenv("HFSQL_USER", "admin")
    password: str = os.getenv("HFSQL_PASSWORD", "")
    
    if host and port and database and user:
        return f"""
        DRIVER={{HFSQL}};Server Name={host};Server Port={port};
        Database={database};UID={user};PWD={password};IntegrityCheck=1
        """
    else:
        print("Erreur: Variables d'environnement manquantes pour la connexion à la base de données.")
        raise ValueError("Missing environment variables for database connection.")
    

        
@DatabaseConnection.error_handler
@mcp.resource('tables://tables', description="List all tables in the database", mime_type="application/json")
def get_table_names() -> str:
    """List all tables in the database.

    Returns:
        Resource: A resource containing the list of tables names.
    """
    with DatabaseConnection(connection_string=connection_string()) as conn:
        cursor: pypyodbc.Cursor = conn.cursor
        tables: list = [table[2] for table in cursor.tables()]

        return json.dumps(tables)
    

@DatabaseConnection.error_handler
@mcp.resource('tables://{table_name}/columns', description="List all columns in a table as a list of resources")
def get_table_columns(table_name: str) -> list[Resource]:
    """List all columns in a table as a list of resources.

    Args:
        table_name (str): The name of the table to list columns from.

    Returns:
        list[Resource]: A list of resources containing the list of columns informations.
    """
    with DatabaseConnection(connection_string=connection_string()) as conn:
        cursor = conn.cursor
        columns: list[Resource] = []
        # Get the the name of each column in the table as list of strings
        for column_info in cursor.columns(table=table_name):
            column_name = str(column_info[1]) if column_info[1] else ""
            resource: Resource = Resource(
            uri=AnyUrl(f'tables://{table_name}/columns/{column_name}'),
            name=column_name,
            description=str(column_info[9]) if column_info[9] else "",)
            columns.append(resource)

    return columns

@DatabaseConnection.error_handler
@mcp.tool(name="list_tables", description="List all tables in the database")
def get_tables() -> str:
    """List all tables in the database.

    Returns:
        str: A JSON string containing the list of tables names.
    """
    with DatabaseConnection(connection_string=connection_string()) as conn:
        cursor = conn.cursor
        tables: list[str | None] = []

        # Loop over the tables in the database
        for table_info in cursor.tables():
            tables.append(table_info[2])

    return json.dumps(tables)

@DatabaseConnection.error_handler
@mcp.tool(name="list_columns", description="List all columns in a table")
def get_column_names(table_name: str) -> str:
    """List all columns in a table.

    Args:
        table_name (str): The name of the table to list columns from.

    Returns:
        str: A JSON string containing the list of columns names.
    """
    with DatabaseConnection(connection_string=connection_string()) as conn:
        cursor = conn.cursor
        columns: list[dict[str, Any]] = []

        # Get the the name of each column in the table as list of strings
        for column_info in cursor.columns(table=table_name):
            if column_info[1]:  # Ensure the column index exists
                columns.append({
                    "name": str(column_info[1]),
                    "type": str(column_info[3]) if column_info[3] else "",
                    "description": str(column_info[9]) if column_info[9] else ""
                })
    
    return json.dumps(columns)


@DatabaseConnection.error_handler
@mcp.tool(name="select_query", description="Execute a select query")
def execute_select_query(query:str, params:tuple = ()) -> str:
    """Execute a select query and return the result as a JSON object.

    Args:
        query (str): The select query to execute.
        params (tuple): The parameters to use in the query.

    Returns:
        json: The result of the query as a JSON object.
    """
    if not query.lower().startswith("select"):
        return "Query must start with 'SELECT'"
    
    if query.find(";") > 1:
        return "Query must not contain ';'"
    
    with DatabaseConnection(connection_string=connection_string()) as conn:
        cursor = conn.cursor
        cursor.execute(query, params)
        
        # Fetch all rows from the executed query
        rows = cursor.fetchall()
        
        # Get column names from cursor description
        if cursor.description is None:
            return "No results found."
        
        columns = [column[0] for column in cursor.description]
        
        # Convert rows to list of dictionaries
        result = [dict(zip(columns, row)) for row in rows]
    
    return json.dumps(result)


@DatabaseConnection.error_handler
@mcp.tool(name="insert_query", description="Execute an insert query")
def execute_insert_query(query:str, params:tuple=()) -> str:
    """Execute an insert query.

    Args:
        query (str): The insert query to execute.
        params (tuple): The parameters to use in the query.

    Returns:
        str: A message indicating the resu lt of the operation.
    """
    if not query.lower().startswith("insert"):
        return "Query must start with 'INSERT'"
    
    if query.find(";") > 1:
        return "Query must not contain ';'"
    
    with DatabaseConnection(connection_string=connection_string()) as conn:
        cursor = conn.cursor
        cursor.execute(query, params=params)
        
        # Commit the changes to the database
        cursor.commit()
    
    return "Insert operation completed successfully."


@DatabaseConnection.error_handler
@mcp.tool(name="update_query", description="Execute an update query")
def execute_update_query(query:str, params:tuple) -> str:
    """Execute an update query.

    Args:
        query (str): The update query to execute.
        params (tuple): The parameters to use in the query.

    Returns:
        str: A message indicating the result of the operation.
    """
    if not query.lower().startswith("update"):
        return "Query must start with 'UPDATE'"
    
    if query.find(";") > 1:
        return "Query must not contain ';'"
    
    with DatabaseConnection(connection_string=connection_string()) as conn:
        cursor = conn.cursor
        cursor.execute(query, params=params)
        
        # Commit the changes to the database
        cursor.commit()
    
    return "Update operation completed successfully."


@mcp.prompt(name="help_build_query", description="Help the user build a query")
def prompt_build_query(table_name: str) -> list[base.Message]:
    """Prompt the user for help in building a query.

    Args:
        table_name (str): The name of the table to build a query for.

    Returns:
        list[base.Message]: A list of messages to guide the user in building a query.
    """
    return [
        base.AssistantMessage(f"Je vois que vous travaillez avec la table {table_name}. Comment puis-je vous aider à construire votre requête?"),
        base.UserMessage("Je voudrais filtrer les données par..."),
        base.AssistantMessage("Je peux vous aider avec ça. Quels champs souhaitez-vous utiliser pour le filtrage?")
    ]


@mcp.prompt(name="explore_data", description="Explore the data in a table")
def prompt_explore_data(table_name: str) -> list[base.Message]:
    return [
        base.AssistantMessage(f"Explorons ensemble les données de la table {table_name}."),
        base.AssistantMessage("Souhaitez-vous voir:\n- Les premières lignes\n- Des statistiques descriptives\n- La distribution des valeurs\n- Des corrélations entre colonnes?")
    ]

@mcp.prompt(name="use_database_schema", description="Use the database schema")
def prompt_use_database_schema() -> list[base.Message]:
    """Prompt the user to use the database schema.

    Returns:
        list[base.Message]: A list of messages to guide the user in using the database schema.
    """
    return [
        base.UserMessage("Utilisez la commande /list_tables pour explorer le schéma de la base de données"),
        base.AssistantMessage("Je peux vous aider à explorer votre base de données. Voulez-vous voir la liste des tables disponibles?")
    ]

if __name__ == "__main__":
    print(get_tables())