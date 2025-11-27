import psycopg2
from psycopg2 import sql
from db_config import DB_PARAMS

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(**DB_PARAMS)
        except psycopg2.OperationalError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            self.conn = None

    def close(self):
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None, fetch=None):
        if not self.conn:
            print("Нет соединения с базой данных.")
            return None
        
        with self.conn.cursor() as cursor:
            try:
                cursor.execute(query, params)
                if fetch == "one":
                    return cursor.fetchone()
                if fetch == "all":
                    return cursor.fetchall()
                self.conn.commit()
                return True # Для INSERT, UPDATE, DELETE
            except psycopg2.Error as e:
                self.conn.rollback()
                print(f"Ошибка выполнения запроса: {e}")
                return None

    def get_column_names(self, table_name):
        query = sql.SQL("SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position")
        return [row[0] for row in self.execute_query(query, (table_name,), fetch="all")]