FastAPI Shipment API — Learning Project

This project documents my progress in learning FastAPI and backend development fundamentals.

What I have learned so far

* Creating FastAPI routes and endpoint functions
* Understanding path, query, and request-body parameters
* Validating request data with Pydantic models
* Separating create, read, and update schemas
* Restricting shipment statuses with Python Enum
* Handling errors with HTTPException
* Implementing CRUD operations:
    * Create shipments with POST
    * Read shipments with GET
    * Update shipment status with PATCH
    * Delete shipments with DELETE
* Converting Pydantic models into dictionaries with model_dump()
* Loading a list of shipment records from a JSON file
* Converting that list into a dictionary indexed by shipment ID
* Saving POST, PATCH, and DELETE changes back to the JSON file
* Separating API routes, schemas, and data-storage logic into different Python modules

Current storage approach

The application currently uses shipments.json for persistent storage.

When the application starts:

1. data.py reads the JSON file.
2. json.load() converts the JSON data into Python data.
3. A loop creates an in-memory dictionary indexed by shipment ID.
4. The API endpoints use that dictionary while the server is running.

After a POST, PATCH, or DELETE operation, the save() function converts the dictionary back into a list and writes the updated records to shipments.json.

Next learning stage

The next step is replacing JSON file storage with SQLite. This will help me understand:

* Database tables and records
* Primary keys
* Database connections and sessions
* Creating, querying, updating, and deleting database rows
* Connecting FastAPI endpoints to a relational database
* Separating API schemas from database models
