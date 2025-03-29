from typing import Optional
from mcp.types import Resource
from mcp.server.fastmcp import FastMCP
import json 

from db_connect import connect_to_db

mcp = FastMCP("Demo")

        
@mcp.resource('tables://list-tables', description="List all tables in the database", mime_type="application/json")
def list_tables() -> Resource:
    """List all tables in the database.

    Returns:
        Resource: A resource containing the list of tables names.
    """
    try:
        conn = connect_to_db()
    except Exception as e:
        return str(e)
    cursor = conn.cursor()
    
    tables: list[str] = []
    
    # Loop over the tables in the database and append their names to the list
    tables = [table[2] for table in cursor.tables()]
    
    conn.close()
    return json.dumps(tables)


@mcp.resource('tables://table-columns/{table_name}', description="List all columns in a table as a list of resources")
def table_columns_resource(table_name: str) -> list[Resource]:
    """List all columns in a table as a list of resources.

    Args:
        table_name (str): The name of the table to list columns from.

    Returns:
        list[Resource]: A list of resources containing the list of columns informations.
    """
    try:
        conn = connect_to_db()
    except Exception as e:
        return str(e)
    
    cursor = conn.cursor()
    columns: list[Resource] = []
    # Get the the name of each column in the table as list of strings
    for column_info in cursor.columns(table=table_name):
        resource: Resource = Resource(
        uri=f'tables://table-columns/{table_name}/{column_info[1]}',
        name=column_info[1],
        description=column_info[9],)
        columns.append(resource)
    
    conn.close()
    return columns

@mcp.tool()
def select_query(query:str) -> json:
    """Execute a select query and return the result as a JSON object.

    Args:
        query (str): The select query to execute.

    Returns:
        json: The result of the query as a JSON object.
    """
    if not query.lower().startswith("select"):
        return "Query must start with 'SELECT'"
    
    try:
        conn = connect_to_db()
    except Exception as e:
        return str(e)
    
    cursor = conn.cursor()
    cursor.execute(query)
    
    # Fetch all rows from the executed query
    rows = cursor.fetchall()
    
    # Get column names from cursor description
    columns = [column[0] for column in cursor.description]
    
    # Convert rows to list of dictionaries
    result = [dict(zip(columns, row)) for row in rows]
    
    conn.close()
    return json.dumps(result)


@mcp.tool()
def insert_query(query:str) -> str:
    """Execute an insert query.

    Args:
        query (str): The insert query to execute.

    Returns:
        str: A message indicating the result of the operation.
    """
    if not query.lower().startswith("insert"):
        return "Query must start with 'INSERT'"
    
    try:
        conn = connect_to_db()
    except Exception as e:
        return str(e)
    
    cursor = conn.cursor()
    cursor.execute(query)
    
    # Commit the changes to the database
    conn.commit()
    
    conn.close()
    return "Insert operation completed successfully."

if __name__ == "__main__":
    try:
        conn = connect_to_db()
    except Exception as e:
        print(e)
    
    cursor = conn.cursor()
    
    # tables: list[str] = []
    # for table in cursor.tables():
    #     tables.append(table[2])
    
    # print( ' '.join([str(x) for x in tables]))
    
    # columns = []
    # for column_info in cursor.columns(table='Client'):
    #     columns.append(column_info[1])
    # conn.close()
    # print( ' '.join([str(x) for x in columns]))
    
    print(select_query("SELECT * FROM Client"))