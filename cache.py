import sqlite3
from sqlite3 import Cursor


class Cache:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('.cache')

    def __enter__(self) -> Cursor:
        cursor: Cursor = self.conn.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS cache (
            url TEXT PRIMARY KEY,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")

        return cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()


def check_cache(url: str) -> tuple | None:
    with Cache() as cursor:
        cursor.execute('SELECT content FROM cache WHERE url = ?', (url,))
        return cursor.fetchone()


def store_cache(url: str, content: bytes) -> None:
    with Cache() as cursor:
        cursor.execute('INSERT INTO cache (url, content) VALUES (?, ?)', (url, content))
