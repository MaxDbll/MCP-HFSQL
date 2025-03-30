from typing import Optional
from mcp.types import Resource
from mcp.server.fastmcp import FastMCP
import json 

from mcp.server.fastmcp.prompts import base
import pypyodbc

from db_connect import DatabaseConnection

mcp = FastMCP("Demo", dependencies=["pypyodbc"])

def connection_string():
    return """
    DRIVER={HFSQL};Server Name=127.0.0.1;Server Port=4900;
    Database=python_odbc;UID=admin;IntegrityCheck=1
            """
        
@DatabaseConnection.error_handler
@mcp.resource('tables://list-tables', description="List all tables in the database", mime_type="application/json")
def list_tables() -> Resource:
    """List all tables in the database.

    Returns:
        Resource: A resource containing the list of tables names.
    """
    with DatabaseConnection(connection_string=connection_string()) as conn:
        cursor: pypyodbc.Cursor = conn.cursor
        tables: list[str] = [table[2] for table in cursor.tables()]
    
        return json.dumps(tables)
    

@DatabaseConnection.error_handler
@mcp.resource('tables://table-columns/{table_name}', description="List all columns in a table as a list of resources")
def table_columns_resource(table_name: str) -> list[Resource]:
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
            resource: Resource = Resource(
            uri=f'tables://table-columns/{table_name}/{column_info[1]}',
            name=column_info[1],
            description=column_info[9],)
            columns.append(resource)
    
    return columns

@DatabaseConnection.error_handler
@mcp.tool(name="list_tables", description="List all tables in the database")
def list_tables_tool() -> str:
    """List all tables in the database.

    Returns:
        str: A JSON string containing the list of tables names.
    """
    with DatabaseConnection(connection_string=connection_string()) as conn:
        cursor = conn.cursor
        tables: list[str] = []

        # Loop over the tables in the database
        for table_info in cursor.tables():
            tables.append(table_info[2])
    
    return json.dumps(tables)

@DatabaseConnection.error_handler
@mcp.tool(name="list_tables_with_columns", description="List all tables in the database along with their columns")
def list_tables_with_columns() -> str:
    """List all tables in the database along with their columns.

    Returns:
        str: A JSON string containing the list of tables and their columns.
    """
    with DatabaseConnection(connection_string=connection_string()) as conn:
        cursor = conn.cursor
        tables_with_columns = {}

        # Loop over the tables in the database
        for table_info in cursor.tables():
            table_name = table_info[2]
            columns = [column_info[1] for column_info in cursor.columns(table=table_name)]
            tables_with_columns[table_name] = columns
    
    return json.dumps(tables_with_columns)

@DatabaseConnection.error_handler
@mcp.tool(name="list_columns", description="List all columns in a table")
def list_columns(table_name: str) -> str:
    """List all columns in a table.

    Args:
        table_name (str): The name of the table to list columns from.

    Returns:
        str: A JSON string containing the list of columns names.
    """
    with DatabaseConnection(connection_string=connection_string()) as conn:
        cursor = conn.cursor
        columns: list[str] = []

        # Get the the name of each column in the table as list of strings
        for column_info in cursor.columns(table=table_name):
            columns.append(column_info[1])
    
    return json.dumps(columns)


@DatabaseConnection.error_handler
@mcp.tool(name="select_query", description="Execute a select query")
def select_query(query:str) -> json:
    """Execute a select query and return the result as a JSON object.

    Args:
        query (str): The select query to execute.

    Returns:
        json: The result of the query as a JSON object.
    """
    if not query.lower().startswith("select"):
        return "Query must start with 'SELECT'"
    
    with DatabaseConnection(connection_string=connection_string()) as conn:
        cursor = conn.cursor
        cursor.execute(query)
        
        # Fetch all rows from the executed query
        rows = cursor.fetchall()
        
        # Get column names from cursor description
        columns = [column[0] for column in cursor.description]
        
        # Convert rows to list of dictionaries
        result = [dict(zip(columns, row)) for row in rows]
    
    return json.dumps(result)


@DatabaseConnection.error_handler
@mcp.tool(name="insert_query", description="Execute an insert query")
def insert_query(query:str) -> str:
    """Execute an insert query.

    Args:
        query (str): The insert query to execute.

    Returns:
        str: A message indicating the result of the operation.
    """
    if not query.lower().startswith("insert"):
        return "Query must start with 'INSERT'"
    
    with DatabaseConnection(connection_string=connection_string()) as conn:
        cursor = conn.cursor
        cursor.execute(query)
        
        # Commit the changes to the database
        conn.commit()
    
    return "Insert operation completed successfully."


@mcp.prompt(name="help_build_query", description="Help the user build a query")
def help_build_query(table_name: str) -> list[base.Message]:
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
def explore_data(table_name: str) -> list[base.Message]:
    return [
        base.AssistantMessage(f"Explorons ensemble les données de la table {table_name}."),
        base.AssistantMessage("Souhaitez-vous voir:\n- Les premières lignes\n- Des statistiques descriptives\n- La distribution des valeurs\n- Des corrélations entre colonnes?")
    ]

@mcp.prompt(name="use_database_schema", description="Use the database schema")
def use_database_schema() -> list[base.Message]:
    """Prompt the user to use the database schema.

    Returns:
        list[base.Message]: A list of messages to guide the user in using the database schema.
    """
    return [
        base.SystemMessage("Utilisez la commande /list_tables pour explorer le schéma de la base de données"),
        base.AssistantMessage("Je peux vous aider à explorer votre base de données. Voulez-vous voir la liste des tables disponibles?")
    ]

if __name__ == "__main__":
    print(list_tables())
