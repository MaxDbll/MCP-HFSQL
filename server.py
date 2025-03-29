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
    for table in cursor.tables():
        tables.append(table[2])
    
    conn.close()
    return json.dumps(tables)


@mcp.resource('tables://table-columns/{table_name}', description="List all columns in a table", mime_type="application/json")
def table_columns(table_name: str) -> Resource:
    """List all columns in a table.

    Args:
        table_name (str): The name of the table to list columns from.

    Returns:
        Resource: A resource containing the list of columns names.
    """
    try:
        conn = connect_to_db()
    except Exception as e:
        return str(e)
    
    cursor = conn.cursor()
    columns: list[str] = []
    # Get the the name of each column in the table as list of strings
    columns = list(map(lambda column_info: column_info[1], cursor.columns(table=table_name)))
    
    conn.close()
    return json.dumps(columns)


@mcp.resource('tables://table-columns-resource/{table_name}', description="List all columns in a table as a list of resources")
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
    
    table_columns_resource('Client')