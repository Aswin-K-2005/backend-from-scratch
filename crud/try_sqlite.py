import sqlite3

conn = sqlite3.connect("test.db")
conn.row_factory = sqlite3.Row

conn.execute("""CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL)
                """)
cur = conn.execute(
    """
            INSERT INTO users (name,email) VALUES (?,?) 
""",
    ("Aswin", "idk@gmail.com"),
)
print(cur.lastrowid)
conn.commit()

cur = conn.execute(
    """
            INSERT INTO users (name,email) VALUES (?,?) 
""",
    ("Aswin2", "idk1@gmail.com"),
)
print(cur.lastrowid)
conn.commit()

rows = conn.execute("SELECT * from users")

for r in rows:
    print(dict(r))

row = conn.execute("SELECT * from users where id == ?", (cur.lastrowid,)).fetchone()
print(dict(row))


curr = conn.execute(
    "UPDATE users SET email = ? WHERE id == ?", ("hi@gmail.com", cur.lastrowid)
)
print(curr.rowcount)
conn.execute("DELETE FROM users where id == ?", (1,))
conn.commit()

rows = conn.execute("SELECT * FROM users")
for row in rows:
    print(dict(row))
x = 3
r = conn.execute(f"SELECT * from users WHERE id == {x}").fetchone()
if r is not None:
    print(dict(r))
else:
    print("NONE")
r = conn.execute("SELECT * FROM users WHERE id == ? ", (x,)).fetchone()
if r is not None:
    print(dict(r))
else:
    print("NONE")

evil = "x' OR '1'='1"
r = conn.execute(f"SELECT * FROM users WHERE name = '{evil}'").fetchall()
print(len(r))  # expect: every user
r = conn.execute("SELECT * FROM users WHERE name = ?", (evil,)).fetchall()
print(len(r))  # expect: 0
