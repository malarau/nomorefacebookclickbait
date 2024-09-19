import sqlite3, os, psycopg2
from abc import ABC, abstractmethod
from app.logger_config import app_logger

class DatabaseFactory:
    @staticmethod
    def create_database(docker_env):
        return FacebookDatabaseSQLite()

        # To try in the future
        """        
        if docker_env:
            return FacebookDatabasePostgres()
        else:
            return FacebookDatabaseSQLite()
        """
        # Add the following to docker-compose.yml... and test it
        """
        db:
            image: postgres
            restart: always
            env_file:
            - .env
            environment:
            - DATABASE_HOST=127.0.0.1
            ports:
            - '5432:5432'
            volumes:
            - ./app/database/data:/var/lib/postgresql/data
            healthcheck:
            test: ["CMD-SHELL", "pg_isready -d ${POSTGRES_DB} -U ${POSTGRES_USER}"]
            interval: 2s
            timeout: 5s
            retries: 10

        # And to scraper:

        scraper:
            depends_on:
                db:
                    condition: service_healthy
        """
        
class FacebookDatabase(ABC):
    def __init__(self):
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_table()

    @abstractmethod
    def _connect(self):
        pass

    @abstractmethod
    def _execute_query(self, query, params=()):
        pass

    @abstractmethod
    def insert_post(self, post_id, date, page, success):
        pass

    @abstractmethod
    def update_post_success(self, post_id, success):
        pass

    def _create_table(self):
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS processed_posts (
            id TEXT PRIMARY KEY,
            date TEXT,
            page TEXT,
            success INTEGER
        );
        '''
        self._execute_query(create_table_sql)

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

class FacebookDatabaseSQLite(FacebookDatabase):
    def _connect(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_path, 'data.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def _execute_query(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except sqlite3.Error as e:
            app_logger.error(e)
            self.conn.rollback()
            raise e

    def insert_post(self, post_id, date, page, success):
        query = 'INSERT INTO processed_posts (id, date, page, success) VALUES (?, ?, ?, ?)'
        try:
            self._execute_query(query, (post_id, date, page, success))
            return True
        except Exception as e:
            app_logger.error(e)
            return False  # post id already exists

    def update_post_success(self, post_id, success):
        query = 'UPDATE processed_posts SET success = ? WHERE id = ?'
        try:
            self._execute_query(query, (success, post_id))
            return True
        except Exception as e:
            app_logger.error(e)
            return False

class FacebookDatabasePostgres(FacebookDatabase):
    def _connect(self):
        try:
            conn_str = f"dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}"
            self.conn = psycopg2.connect(conn_str)
            self.cursor = self.conn.cursor()
        except Exception as e:
            app_logger.error(e)
            raise

    def _execute_query(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except psycopg2.Error as e:
            app_logger.error(e)
            self.conn.rollback()
            raise e

    def insert_post(self, post_id, date, page, success):
        query = 'INSERT INTO processed_posts (id, date, page, success) VALUES (%s, %s, %s, %s)'
        try:
            self._execute_query(query, (post_id, date, page, success))
            return True
        except Exception as e:
            app_logger.error(e)
            return False  # post id already exists

    def update_post_success(self, post_id, success):
        query = 'UPDATE processed_posts SET success = %s WHERE id = %s'
        try:
            self._execute_query(query, (success, post_id))
            return True
        except Exception as e:
            app_logger.error(e)
            return False