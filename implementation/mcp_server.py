import json
from fastmcp import FastMCP
from db import SQLiteAdapter, ValidationError

mcp = FastMCP("SQLite Lab MCP Server")
adapter = SQLiteAdapter()


@mcp.tool(name="search")
def search(
    table: str,
    columns: list[str] | None = None,
    filters: list[dict] | None = None,
    limit: int = 20,
    offset: int = 0,
    order_by: str | None = None,
    descending: bool = False,
) -> str:
    """Search rows in a database table with optional filters, column selection, ordering, and pagination.
    
    filters format: [{"column": "cohort", "operator": "=", "value": "A1"}]
    Supported operators: =, !=, >, <, >=, <=, LIKE
    """
    try:
        rows = adapter.search(table, columns, filters, limit, offset, order_by, descending)
        return json.dumps({"rows": rows, "count": len(rows)}, default=str)
    except ValidationError as e:
        return json.dumps({"error": str(e)})


@mcp.tool(name="insert")
def insert(table: str, values: dict) -> str:
    """Insert a single row into a database table.
    
    values format: {"name": "Frank", "cohort": "A2", "email": "frank@example.com"}
    """
    try:
        result = adapter.insert(table, values)
        return json.dumps({"inserted": result}, default=str)
    except ValidationError as e:
        return json.dumps({"error": str(e)})


@mcp.tool(name="aggregate")
def aggregate(
    table: str,
    metric: str,
    column: str | None = None,
    filters: list[dict] | None = None,
    group_by: str | None = None,
) -> str:
    """Run an aggregate query (count, avg, sum, min, max) on a table.
    
    Example: metric="avg", column="score", table="enrollments", group_by="student_id"
    """
    try:
        rows = adapter.aggregate(table, metric, column, filters, group_by)
        return json.dumps({"metric": metric, "results": rows}, default=str)
    except ValidationError as e:
        return json.dumps({"error": str(e)})


@mcp.resource("schema://database")
def database_schema() -> str:
    """Return the full database schema for all tables."""
    tables = adapter.list_tables()
    schema = {}
    for t in tables:
        schema[t] = adapter.get_table_schema(t)
    return json.dumps(schema, indent=2)


@mcp.resource("schema://table/{table_name}")
def table_schema(table_name: str) -> str:
    """Return the schema for a single table."""
    try:
        cols = adapter.get_table_schema(table_name)
        return json.dumps({"table": table_name, "columns": cols}, indent=2)
    except ValidationError as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()