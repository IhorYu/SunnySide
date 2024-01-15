import sqlite3


def create_connection(db_file):
    """ Create a database connection to the SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn


def create_table(conn, create_table_sql):
    """ Create a table from the create_table_sql statement """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)


def main():
    database = "telegram_users.db"

    sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                    id integer PRIMARY KEY,
                                    user_id integer NOT NULL
                                ); """

    conn = create_connection(database)
    if conn is not None:
        create_table(conn, sql_create_users_table)
    else:
        print("Error! Cannot create the database connection.")


if __name__ == '__main__':
    main()
