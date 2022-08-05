import sqlite3


class Database:
    def __init__(self, db_file: str, db_name: str):
        self.db_file = db_file
        self.db_name = db_name
        self.conn = self.connect(self.db_file)

    def connect(self, db_file: str):
        """ create a database connection to the SQLite database
            specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        try:
            return sqlite3.connect(db_file)
        except sqlite3.Error as e:
            print(e)

    def create_table(self, table_name: str):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(
                f"CREATE TABLE if not exists {table_name} (id text primary key, content text)")
        except sqlite3.Error as e:
            print(e)

    def insert(self, table_name: str, id: str, content: str):
        """
        Insert a row of data into the table
        :param conn: Connection object
        :param table_name: table name
        :param id: id of the row
        :param content: content of the row
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(f"INSERT INTO {table_name} VALUES (?, ?)", (id, content))
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    def select(self, table_name: str, id: str):
        """
        Query the table
        :param conn: Connection object
        :param table_name: table name
        :param id: id of the row
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(
                f"SELECT * FROM {table_name} WHERE id = ? LIMIT 1", (id,))
            row = c.fetchone()
            return row
        except sqlite3.Error as e:
            print(e)

    # select all the rows in the table
    def select_all(self, table_name: str):
        """
        Query all rows in the table
        :param conn: the Connection object
        :param table_name: the table name
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(f"SELECT * FROM {table_name}")
            rows = c.fetchall()
            return rows
        except sqlite3.Error as e:
            print(e)

    def clear_table(self, table_name: str):
        try:
            c = self.conn.cursor()
            c.execute(f"DELETE FROM {table_name}")
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)
    
    # check if table exists
    def table_exists(self, table_name: str):
        c = self.conn.cursor()
        c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        row = c.fetchone()
        return row is not None

    # check if table is empty
    def is_table_empty(self, table_name: str):
        if not self.table_exists(table_name):
            return True
        c = self.conn.cursor()
        c.execute(f"SELECT * FROM {table_name} LIMIT 1")
        row = c.fetchone()
        return row is None
