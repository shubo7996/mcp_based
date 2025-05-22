import sqlite3
import argparse
from mcp.server.fastmcp import FastMCP

#mcp = FastMCP('sqlite-demo')
mcp = FastMCP(name="news-reader", host="127.0.0.1", port=8000, timeout=30)
def init_db():
    conn = sqlite3.connect('demo.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            profession TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn, cursor

@mcp.tool()
def add_data(query: str) -> bool:
    """
    Add a new person to the 'people' table in the database using a SQL INSERT query.

    The query must insert values for the following columns:
        - name: TEXT (required)
        - age: INTEGER (required)
        - profession: TEXT (required)

    Note: The 'id' field is automatically generated.

    Args:
        query (str): SQL INSERT query. 
            Example:
                INSERT INTO people (name, age, profession)
                VALUES ('Alice Smith', 25, 'Developer')

    Returns:
        bool: True if the record was added successfully, False otherwise.

    Example:
        >>> add_data("INSERT INTO people (name, age, profession) VALUES ('Bob', 40, 'Teacher')")
        True
    """
    conn, cursor = init_db()
    try:
        cursor.execute(query)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error adding data: {e}")
        return False
    finally:
        conn.close()

@mcp.tool()
def read_data(query: str = "SELECT * FROM people") -> list:
    """
    Read one or more records from the 'people' table using a SQL SELECT query.

    This tool is used to retrieve information about individuals from the database.

    Args:
        query (str, optional): SQL SELECT query to specify which fields and conditions to use.
            Defaults to "SELECT * FROM people".
            Examples:
                - SELECT name FROM people WHERE age > 30
                - SELECT * FROM people ORDER BY age DESC

    Returns:
        list: A list of tuples representing the result of the query.

    Example:
        >>> read_data("SELECT name, profession FROM people WHERE age < 30")
        [('Alice Smith', 'Developer')]
    """
    conn, cursor = init_db()
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error reading data: {e}")
        return []
    finally:
        conn.close()


@mcp.tool()
def update_people(query: str = "Update "):
    """
    Update records in the 'people' table using a SQL UPDATE query.

    This tool is used to modify one or more fields for existing records.

    Args:
        query (str): SQL UPDATE query that specifies new values and conditions.
            Example:
                UPDATE people SET age = 27 WHERE name = 'Subhamoy'

    Returns:
        str: A confirmation message or error string.

    Example:
        >>> update_people("UPDATE people SET profession = 'Scientist' WHERE name = 'Alice Smith'")
        "Update successful."
    """
    conn, cursor = init_db()
    try:
        cursor.execute(query)
        conn.commit()
        return "Update Succefully!"
    except sqlite3.Error as e:
        print(f"Error reading data: {e}")
        return []
    finally:
        conn.close()


@mcp.tool()
def delete_person(query: str):
    """
    Delete one or more records from the 'people' table using a SQL DELETE query.

    Use this tool to remove entries that match the specified condition.

    Args:
        query (str): SQL DELETE query.
            Example:
                DELETE FROM people WHERE name = 'Alice Smith'

    Returns:
        str: A message indicating whether the deletion was successful or not.

    Example:
        >>> delete_person("DELETE FROM people WHERE age < 25")
        "Delete successful."
    """
    conn, cursor = init_db()
    try:
        cursor.execute(query)
        conn.commit()
        return "Delete successful."
    except sqlite3.Error as e:
        return f"Error deleting data: {e}"
    finally:
        conn.close()

if __name__ == "__main__":
    # Start the server
    print("🚀Starting server... ")

    # Debug Mode
    #  uv run mcp dev server.py

    # Production Mode
    # uv run server.py --server_type=sse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"]
    )

    args = parser.parse_args()
    mcp.run(args.server_type)

