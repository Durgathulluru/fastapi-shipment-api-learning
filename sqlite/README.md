# SQLite Shipment API Study Notes

This folder is a small FastAPI project that stores shipment data in a local SQLite database.

Files in this folder:

- `main.py`: FastAPI routes/endpoints.
- `database.py`: SQLite connection and CRUD database logic.
- `schemas.py`: Pydantic models used for request and response validation.
- `sqlite.db`: Local database file created by SQLite. This file is ignored by Git.

## Big Picture

The flow looks like this:

```text
Client request
    -> FastAPI endpoint in main.py
    -> Pydantic schema in schemas.py validates the data
    -> Database class in database.py runs SQL
    -> SQLite stores or returns data from sqlite.db
    -> FastAPI sends response back to the client
```

## SQLite Database File

In `database.py`, the database path is:

```python
Path(__file__).with_name("sqlite.db")
```

This means:

- Put the database file in the same folder as `database.py`.
- If `sqlite/sqlite.db` already exists, SQLite opens and uses the existing file.
- If it does not exist, SQLite creates a new file when the app connects.

The database file is ignored in `.gitignore` because it is local runtime data. Usually, source code goes to GitHub, but local database files do not.

## Database Class

`Database` is a helper class that keeps database work in one place.

```python
db = Database()
```

When `Database()` is created, it:

1. Stores the database path in `self.db_path`.
2. Calls `create_table("shipments")`.
3. Makes sure the `shipments` table exists before the API starts using it.

## Connecting to SQLite

The connection is created with:

```python
sqlite3.connect(self.db_path)
```

Important idea:

- A connection opens the database file.
- A cursor runs SQL commands.
- The `with` block helps commit changes and close safely.

Example:

```python
with self.get_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM shipments")
```

## Why Create `conn` in Each Function?

In this project, each database function opens its own connection:

```python
with self.get_connection() as conn:
    cur = conn.cursor()
```

That means `create()`, `get()`, `update()`, and `delete()` each get a fresh `conn`.

This helps avoid a common SQLite thread error:

```text
SQLite objects created in a thread can only be used in that same thread
```

FastAPI can handle different requests in different threads. If the app creates one SQLite connection once and reuses it everywhere, one request might try to use a connection that was created in another thread. SQLite blocks that by default.

Opening a connection inside each database function is safer because:

- The connection is created when that function needs it.
- The connection is used only for that one database operation.
- The `with` block closes it after the work is finished.
- Different API requests do not have to share the same SQLite connection object.

Another option is using:

```python
sqlite3.connect(self.db_path, check_same_thread=False)
```

But for this project, creating a new connection in each function is simpler and safer for learning.

## Why Use `with`?

Using `with self.get_connection() as conn:` is useful because:

- If the code works, SQLite commits the changes.
- If an error happens, SQLite rolls back unfinished changes.
- You do not have to manually call `conn.close()`.
- It reduces database locking problems.

## Creating the Table

The table is created with:

```sql
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id INTEGER PRIMARY KEY,
    origin TEXT,
    destination TEXT,
    content TEXT,
    weight REAL,
    shipment_status TEXT
)
```

Important concepts:

- `CREATE TABLE IF NOT EXISTS` means create the table only if it is missing.
- `INTEGER PRIMARY KEY` is used for the unique shipment id.
- `TEXT` stores string values.
- `REAL` stores decimal numbers like weight.

## CRUD Operations

CRUD means:

- Create
- Read
- Update
- Delete

This project has all four.

## Create Shipment

FastAPI route:

```python
@app.post("/shipments")
```

Database method:

```python
def create(self, shipment: Createshipment)
```

What happens:

1. The request data is validated by `Createshipment`.
2. The shipment is converted to a dictionary using `model_dump()`.
3. The app adds a default status: `placed`.
4. The app finds the current max `shipment_id`.
5. It inserts the new shipment into SQLite.

This line finds the latest id:

```sql
SELECT COALESCE(MAX(shipment_id), 1700) FROM shipments
```

Meaning:

- Get the biggest existing `shipment_id`.
- If there are no rows yet, use `1700`.
- Then the code adds `1`, so the first generated id becomes `1701`.

## Read Shipment

FastAPI route:

```python
@app.get("/shipments")
```

Database method:

```python
def get(self, shipment_id: int)
```

The SQL query is:

```sql
SELECT * FROM shipments WHERE shipment_id = :shipment_id
```

The `:shipment_id` part is a named parameter. It is safer than directly putting user input into SQL strings.

If no shipment is found, the API returns:

```python
HTTPException(status_code=404, detail="Shipment_ID not found")
```

## Update Shipment

FastAPI route:

```python
@app.patch("/shipments/{shipment_id}")
```

Database method:

```python
def update(self, shipment_id: int, shipment: Updateshipment)
```

This line is important:

```python
shipment.model_dump(exclude_unset=True)
```

Meaning:

- Only include fields the user actually sent.
- Useful for PATCH because PATCH usually updates only part of a record.

The SQL update looks like:

```sql
UPDATE shipments SET column = value WHERE shipment_id = :shipment_id
```

## Delete Shipment

FastAPI route:

```python
@app.delete("/shipments/{shipment_id}")
```

Database method:

```python
def delete(self, shipment_id: int)
```

The SQL query is:

```sql
DELETE FROM shipments WHERE shipment_id = :shipment_id
```

Before deleting, the API checks whether the shipment exists. If it does not exist, it returns a 404 error.

## Pydantic Schemas

Schemas are in `schemas.py`.

They define what data is allowed.

### `ShipmentStatus`

```python
class ShipmentStatus(str, Enum):
    PLACED = "placed"
    IN_TRANSIT = "In Transit"
    DELIVERED = "Delivered"
    DELAYED = "Delayed"
```

This limits shipment status to a fixed set of values.

### `Baseshipment`

```python
class Baseshipment(BaseModel):
    content: str = Field(min_length=1, max_length=200)
    origin: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=2, max_length=100)
    weight: float = Field(gt=0, le=40)
```

This contains fields shared by create, read, and update models.

### `Createshipment`

Used when creating a shipment.

```python
class Createshipment(Baseshipment):
    pass
```

The client sends content, origin, destination, and weight. The app adds fields like `shipment_id` and `shipment_status`.

### `Readshipment`

Used when returning shipment data.

```python
class Readshipment(Baseshipment):
    shipment_status: ShipmentStatus
    shipment_id: int
```

This includes fields generated or stored by the system.

### `Updateshipment`

Used when updating a shipment.

```python
class Updateshipment(Baseshipment):
    shipment_status: ShipmentStatus | None = None
    shipment_id: int
```

This model is meant for update data.

## FastAPI Endpoints

Current endpoints:

```text
POST   /shipments
GET    /shipments?shipment_id=1701
PATCH  /shipments/{shipment_id}
DELETE /shipments/{shipment_id}
GET    /scalar
```

`/scalar` opens Scalar API documentation for testing your API in the browser.

## Useful SQL Commands

Create table:

```sql
CREATE TABLE IF NOT EXISTS shipments (...);
```

Insert row:

```sql
INSERT INTO shipments (origin, destination, content, weight, shipment_status)
VALUES (:origin, :destination, :content, :weight, :shipment_status);
```

Select row:

```sql
SELECT * FROM shipments WHERE shipment_id = :shipment_id;
```

Update row:

```sql
UPDATE shipments SET shipment_status = :shipment_status
WHERE shipment_id = :shipment_id;
```

Delete row:

```sql
DELETE FROM shipments WHERE shipment_id = :shipment_id;
```

Drop table:

```sql
DROP TABLE IF EXISTS shipments;
```

## Important Study Points

- SQLite is a file-based database.
- `sqlite3` is Python's built-in SQLite library.
- `Path(__file__).with_name("sqlite.db")` creates or opens `sqlite.db` next to `database.py`.
- `CREATE TABLE IF NOT EXISTS` avoids errors when the table already exists.
- `with conn:` helps commit, rollback, and close safely.
- `cursor.execute()` runs SQL commands.
- Named parameters like `:shipment_id` are safer than string-building user input directly.
- Pydantic models validate API input and shape API output.
- FastAPI routes connect HTTP requests to Python functions.
- `.gitignore` should keep local files like `.db`, `__pycache__`, and `venv` out of GitHub.
