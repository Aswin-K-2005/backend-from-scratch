Allowed = {
    "users": {"id", "name", "email"},
    "events": {"id", "user_id", "type", "details", "created_at"},
}


class CrudBase:
    def __init__(self, conn, table):
        if table not in Allowed:
            raise ValueError("Table not there/Allowed")
        self.conn = conn
        self.table = table
        self.columns = Allowed[table]

    def check_columns(self, data):
        for v in data:
            if v not in self.columns:
                raise ValueError("The coloumn doesnt exist")

    def insert(self, data):
        self.check_columns(data)
        cols = ", ".join(data.keys())
        values = ", ".join(["?"] * len(data))
        cur = self.conn.execute(
            f"INSERT INTO {self.table} ({cols}) VALUES ({values})", tuple(data.values())
        )
        self.conn.commit()
        return cur.lastrowid

    def where_clause(self, where):
        self.check_columns(where)
        if len(where) != 0:
            wh = " WHERE " + " AND ".join(f"{c} = ? " for c in where)
            return (wh, tuple(where.values()))
        else:
            return ("", ())

    def find(self, where):
        sql = f"SELECT * FROM {self.table}"
        part, params = self.where_clause(where)
        row = self.conn.execute(f"{sql} {part}", params).fetchall()
        return [dict(r) for r in row]

    def update(self, where, data):
        sql = f"UPDATE {self.table} SET"
        if not where:
            raise ValueError("Give the condition!")
        if not data:
            raise ValueError("GIve the value to change")
        self.check_columns(data)
        part, params = self.where_clause(where)
        set_part = ", ".join(f"{c} = ?" for c in data)
        curr = self.conn.execute(
            f"{sql} {set_part} {part}", tuple(data.values()) + params
        )
        self.conn.commit()
        return curr.rowcount

    def find_page(self, page, size):
        sql = f"SELECT * from {self.table} ORDER BY id LIMIT ? OFFSET ?"
        if page < 1 or size < 1:
            raise ValueError("value cant be less 1")
        params = (size, (page - 1) * size)
        rows = self.conn.execute(sql, params)
        return [dict(r) for r in rows]

    def delete(self, where):
        sql = f"DELETE from {self.table}"
        if not where:
            raise ValueError("Give the condition!")
        part, params = self.where_clause(where)
        curr = self.conn.execute(f"{sql} {part}", params)
        self.conn.commit()
        return curr.rowcount


if __name__ == "__main__":
    from database import get_connection

    conn = get_connection()
    crud = CrudBase(conn, "users")

    uid = crud.insert({"name": "Aswin", "email": "test@x.com"})
    print(
        crud.find(where={"id": uid})
    )  # [{'id': 1, 'name': 'Aswin', 'email': 'test@x.com'}]
    print(crud.find(where={}))
