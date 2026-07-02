from db import SQLiteAdapter, ValidationError

adapter = SQLiteAdapter()

print("=== 1. List tables ===")
print(adapter.list_tables())

print("\n=== 2. Search students cohort A1 ===")
print(adapter.search("students", filters=[{"column": "cohort", "operator": "=", "value": "A1"}]))

print("\n=== 3. Insert new student ===")
print(adapter.insert("students", {"name": "Frank Do", "cohort": "A2", "email": "frank@example.com"}))

print("\n=== 4. Aggregate: avg score by student ===")
print(adapter.aggregate("enrollments", "avg", "score", group_by="student_id"))

print("\n=== 5. Error: unknown table ===")
try:
    adapter.search("nonexistent")
except ValidationError as e:
    print(f"Caught: {e}")

print("\n=== 6. Error: bad operator ===")
try:
    adapter.search("students", filters=[{"column": "name", "operator": "DROP", "value": "x"}])
except ValidationError as e:
    print(f"Caught: {e}")

print("\n=== 7. Schema resource ===")
for t in adapter.list_tables():
    print(f"  {t}: {[c['name'] for c in adapter.get_table_schema(t)]}")