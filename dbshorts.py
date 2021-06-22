import dbconnect
import traceback

# For GET
def run_selection(statement, params):
    conn = dbconnect.get_db_connection()
    cursor = dbconnect.get_db_cursor(conn)
    result = None

    try:
        cursor.execute(statement, params)
        result = cursor.fetchall()
    except:
        traceback.print_exc()
        print("Some error has occured, I don't freakin know dude")
    dbconnect.close_db_cursor(cursor)
    dbconnect.close_db_connection(conn)
    return result

# For POST
def run_insertion(statement, params):
    conn = dbconnect.get_db_connection()
    cursor = dbconnect.get_db_cursor(conn)
    result = None

    try:
        cursor.execute(statement, params)
        conn.commit()
        result = cursor.lastrowid
    except:
        traceback.print_exc()
        print("Unknown Error has occured")

    dbconnect.close_db_cursor(cursor)
    dbconnect.close_db_connection(conn)
    return result

# For DELETE
def run_deletion(statement, params):
    conn = dbconnect.get_db_connection()
    cursor = dbconnect.get_db_cursor(conn)
    result = None

    try:
        cursor.execute(statement, params)
        conn.commit()
        result = cursor.rowcount
    except:
        traceback.print_exc()
        print("Nani? Bakana, I can't delete?")

    dbconnect.close_db_cursor(cursor)
    dbconnect.close_db_connection(conn)
    return result

# For PATCH
def run_update(statement, params):
    conn = dbconnect.get_db_connection()
    cursor = dbconnect.get_db_cursor(conn)
    result = None

    try:
        cursor.execute(statement, params)
        conn.commit()
        result = cursor.rowcount
    except:
        traceback.print_exc()
        print("Uh oh, I can't update for some reason")

    dbconnect.close_db_cursor(cursor)
    dbconnect.close_db_connection(conn)
    return result