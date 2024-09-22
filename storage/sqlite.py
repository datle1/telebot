
import sqlite3
from storage.storage import Storage


DATABASE_PATH = 'mydatabase.db'

class SqliteStorage(Storage):
    
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.cursor = self.conn.cursor()
        # Create a table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS job (
                id INTEGER PRIMARY KEY,
                days TEXT,
                message TEXT,
                times TEXT,
                status BOOL,
                groups TEXT
            )
        ''')
        self.conn.commit()

    def user_exist(self, user_name):
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (user_name,))
        if self.cursor.fetchone() is not None:
            return True
        else:
            return False
        
    def insert_user(self, user_name):
        self.cursor.execute('INSERT INTO users (username) VALUES (?)', (user_name,))
        self.conn.commit()

    def delete_user(self, user_name):
        self.cursor.execute('DELETE FROM users WHERE username = ?', (user_name,))
        self.conn.commit()

    def get_all_users(self):
        self.cursor.execute('SELECT * from users')
        return self.cursor.fetchall()

    def get_all_jobs(self):
        self.cursor.execute('SELECT * from job')
        return self.cursor.fetchall()
    
    def insert_job(self, days_str, message, times_str, groups):
        self.cursor.execute('INSERT INTO job (days, message, times, status, groups) VALUES (?, ?, ?, ?, ?)',
                        (days_str, message, times_str, True, groups))
        self.conn.commit()

    def delete_job(self, id):
        self.cursor.execute('DELETE FROM job WHERE id = ?', (id,))
        self.conn.commit()

    def get_job_status(self, id):
        self.cursor.execute('SELECT status FROM job WHERE id = ?', (id,))
        return self.cursor.fetchone()

    def switch_job(self, new_status, id):
        self.cursor.execute('UPDATE job SET status = ? WHERE id = ?', (new_status, id,))
        self.conn.commit()