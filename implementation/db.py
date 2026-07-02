import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "lab.db")

ALLOWED_OPERATORS = {"=", "!=", ">", "<", ">=", "<=", "LIKE"}
ALLOWED_METRICS = {"count", "avg", "sum", "min", "max"}


class ValidationError(Exception):
    pass


class SQLiteAdapter:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def list_tables(self):
        conn = self.connect()
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        conn.close()
        return [r["name"] for r in rows]

    def _validate_table(self, table):
        if table not in self.list_tables():
            raise ValidationError(f"Unknown table: {table}")

    def get_table_schema(self, table):
        self._validate_table(table)
        conn = self.connect()
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        conn.close()
        return [
            {"name": r["name"], "type": r["type"], "notnull": bool(r["notnull"]), "pk": bool(r["pk"])}
            for r in rows
        ]

    def _valid_columns(self, table):
        return {col["name"] for col in self.get_table_schema(table)}

    def _validate_columns(self, table, columns):
        valid = self._valid_columns(table)
        for c in columns:
            if c not in valid:
                raise ValidationError(f"Unknown column '{c}' in table '{table}'")

    def search(self, table, columns=None, filters=None, limit=20, offset=0, order_by=None, descending=False):
        self._validate_table(table)
        valid_cols = self._valid_columns(table)

        # columns
        if columns:
            self._validate_columns(table, columns)
            select = ", ".join(columns)
        else:
            select = "*"

        sql = f"SELECT {select} FROM {table}"
        params = []

        # filters
        if filters:
            clauses = []
            for f in filters:
                col, op, val = f.get("column"), f.get("operator", "=").upper(), f.get("value")
                if col not in valid_cols:
                    raise ValidationError(f"Unknown filter column '{col}'")
                if op not in ALLOWED_OPERATORS:
                    raise ValidationError(f"Unsupported operator '{op}'")
                clauses.append(f"{col} {op} ?")
                params.append(val)
            sql += " WHERE " + " AND ".join(clauses)

        # order
        if order_by:
            if order_by not in valid_cols:
                raise ValidationError(f"Unknown order_by column '{order_by}'")
            sql += f" ORDER BY {order_by} {'DESC' if descending else 'ASC'}"

        sql += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        conn = self.connect()
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def insert(self, table, values):
        if not values:
            raise ValidationError("Cannot insert empty values")
        self._validate_table(table)
        self._validate_columns(table, values.keys())

        cols = ", ".join(values.keys())
        placeholders = ", ".join(["?"] * len(values))
        sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"

        conn = self.connect()
        cursor = conn.execute(sql, list(values.values()))
        conn.commit()
        inserted_id = cursor.lastrowid
        conn.close()
        return {"id": inserted_id, **values}

    def aggregate(self, table, metric, column=None, filters=None, group_by=None):
        metric = metric.lower()
        if metric not in ALLOWED_METRICS:
            raise ValidationError(f"Unsupported metric '{metric}'. Allowed: {ALLOWED_METRICS}")
        self._validate_table(table)
        valid_cols = self._valid_columns(table)

        if metric == "count":
            target = column if column and column in valid_cols else "*"
        else:
            if not column or column not in valid_cols:
                raise ValidationError(f"Column required for '{metric}' aggregate")
            target = column

        sql = f"SELECT {metric.upper()}({target}) AS value"

        if group_by:
            if group_by not in valid_cols:
                raise ValidationError(f"Unknown group_by column '{group_by}'")
            sql = f"SELECT {group_by}, {metric.upper()}({target}) AS value"

        sql += f" FROM {table}"
        params = []

        if filters:
            clauses = []
            for f in filters:
                col, op, val = f.get("column"), f.get("operator", "=").upper(), f.get("value")
                if col not in valid_cols:
                    raise ValidationError(f"Unknown filter column '{col}'")
                if op not in ALLOWED_OPERATORS:
                    raise ValidationError(f"Unsupported operator '{op}'")
                clauses.append(f"{col} {op} ?")
                params.append(val)
            sql += " WHERE " + " AND ".join(clauses)

        if group_by:
            sql += f" GROUP BY {group_by}"

        conn = self.connect()
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]