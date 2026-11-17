import sqlite3


def get_connection():
    conn = sqlite3.connect("crud.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("""CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE
                     ) """)
    conn.execute("""CREATE TABLE IF NOT EXISTS events(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    type TEXT NOT NULL,
                    details TEXT,
                    created_at REAL NOT NULL
                     ) """)
    conn.commit()
    return conn


if __name__ == "__main__":
    conn = get_connection()
    print(conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
