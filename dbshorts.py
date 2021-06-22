import dbconnect
import traceback

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