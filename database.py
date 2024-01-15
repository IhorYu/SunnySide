import sqlite3

from decouple import config


# Establish a connection to the SQLite database
def create_connection(db_file):
    """ Create a database connection to the SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn


# Create a table using the provided SQL statement
def create_table(conn, create_table_sql):
    """ Create a table from the create_table_sql statement """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)


# Add a new user to the database
def add_user_to_db(user_id):
    """ Add a new user to the database with a default prompt """
    database = "telegram_users.db"
    conn = create_connection(database)
    if conn:
        sql = ''' INSERT INTO users(user_id, prompt) VALUES(?, ?) '''
        cur = conn.cursor()
        # Setting a default prompt for the new user
        cur.execute(sql, (user_id, config('PROMPT')))
        conn.commit()
        return cur.lastrowid


# Retrieve the current prompt for a user
def get_user_prompt(conn, user_id):
    """ Get current user prompt """
    try:
        cur = conn.cursor()
        cur.execute("SELECT prompt FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else None
    except sqlite3.Error as e:
        print(e)
        return None


# Update the prompt for a user
def update_user_prompt(conn, user_id, prompt):
    """ Update user prompt """
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET prompt = ? WHERE user_id = ?", (prompt, user_id))
        conn.commit()
    except sqlite3.Error as e:
        print(e)


# Main function to initialize the database
def main():
    database = "telegram_users.db"

    sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                        id integer PRIMARY KEY,
                                        user_id integer NOT NULL,
                                        prompt text
                                    ); """

    conn = create_connection(database)
    if conn is not None:
        create_table(conn, sql_create_users_table)
    else:
        print("Error! Cannot create the database connection.")


# Entry point check
if __name__ == '__main__':
    main()
