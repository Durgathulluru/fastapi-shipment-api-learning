from typing import Any, Dict
from pathlib import Path
import sqlite3

from schemas import Createshipment, ShipmentStatus, Updateshipment

class Database:
    def __init__(self, db_path: str | Path = Path(__file__).with_name("sqlite.db")):
   # def __init__(self, db_path: str):
        self.db_path = db_path
        self.create_table("shipments")
        # self.drop_table("shipments")
        
    def drop_table(self, table_name: str):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"DROP TABLE IF EXISTS {table_name}")
        return f"Table {table_name} dropped successfully"

    def get_connection(self):
        #print("Using DB:", Path(self.db_path).resolve())
        return sqlite3.connect(self.db_path)
    
# if __name__ == "__main__":
#     db = Database()
#     db.get_connection()

    def create_table(self, table_name: str):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    shipment_id INTEGER PRIMARY KEY,
                    origin TEXT,
                    destination TEXT,
                    content TEXT,
                    weight REAL,
                    shipment_status TEXT
                )
            """)
            return (f"{table_name} table created successfully")

    def create(self, shipment: Createshipment) -> Dict[str, Any]:
        data = shipment.model_dump()
        data["shipment_status"] = ShipmentStatus.PLACED.value
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute ("SELECT COALESCE(MAX(shipment_id), 1700) FROM shipments")
            row = cur.fetchone()
            max_id = row[0] + 1 
            columns = ', '.join(data.keys())
            values = ', '.join(f":{key}" for key in data.keys())
            data["shipment_id"] = max_id
            cur.execute (f"INSERT INTO shipments ({columns}) VALUES ({values}) ",
                         dict(data)
                         )
        return data
        
    def get(self, shipment_id: int):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute ("""
                         SELECT * FROM shipments WHERE shipment_id = :shipment_id""", 
                         {"shipment_id": shipment_id})
            row = cur.fetchone()
            if row is None:
                return None
            return dict(row)
        
    def update(self, shipment_id:int, shipment:Updateshipment):
        data =shipment.model_dump(exclude_unset=True) # exclude_unset will exclude any fields that are not set
        with self.get_connection() as conn:
            cur = conn.cursor()
            columns = ', '.join(f"{key} = :{key}" for key in data.keys())
            data["shipment_id"] = shipment_id
            cur.execute (f"UPDATE shipments SET {columns} WHERE shipment_id = :shipment_id", dict(data))
        return self.get(shipment_id)
    def delete(self, shipment_id: int):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM shipments WHERE shipment_id = :shipment_id", {"shipment_id": shipment_id})
        return {"message": f"shipment_id: {shipment_id} is sucessfully deleted"}



    
#make the connection to the database
#connection =sqlite3.connect("sqlite.db")
# cursor method acts as a pointer to the database, 
# it opens database, and allows you to execute SQL commands
#cursor = connection.cursor()

#Why use: **"with"** and create table
        #You do not need to manually write connection.close().
        # If your code finishes normally, SQLite commits the changes.
        # If an error happens, SQLite rolls back the unfinished changes.
        # It reduces the chance of leaving the database connection open.
        # It helps avoid “database is locked” problems.
        # The code is cleaner and easier to read.
        # It is safer for beginners because there is less cleanup code to forget
        # with connection:
        #     cursor.execute("""
        #         CREATE TABLE if not exists shipments 
        #                 (
        #                 id INTEGER PRIMARY KEY, 
        #                 origin TEXT, 
        #                 destination TEXT,
        #                 content TEXT,
        #                 weight REAL,
        #                 status TEXT
        #                 )
        #                 """)

#If you do not use with it is a **manual process without with** and you have to remember to close the connection:
        #Possible problems:
        # If an error happens before connection.close(), the connection may stay open.
        # If you forget connection.commit(), your changes may not be saved.
        # If you forget connection.close(), the database file may stay locked.
        # Your code has more manual cleanup to manage.
         
         # CODE:

            # cursor.execute("""
            #     CREATE TABLE if not exists shipments 
            #                 (
            #                 id INTEGER, 
            #                 origin TEXT, 
            #                 destination TEXT,
            #                 weight REAL
            #                 )
            #                 """)
            # connection.close() -- Close the connection to the database


# Better manual version using **try/finally**
        # try:
        #     cursor = connection.cursor()
        #     # database work here
        #     connection.commit()
        # finally:
        #     connection.close()
        # try:
        #    cursor.execute("""
        #    CREATE TABLE if not exists shipments 
        #                 (
        #                 id INTEGER, 
        #                 origin TEXT, 
        #                 destination TEXT,
        #                 weight REAL
        #                 )
        #                 """)
        # finally:
        #     connection.close()


# To **Drop the table**  Shipments and **create shipments table**
        # with connection:
        #     cursor.execute("DROP TABLE shipments")
        #     cursor.execute("""
        #     CREATE TABLE if not exists shipments 
        #                 (
        #                 id INTEGER, 
        #                 origin TEXT, 
        #                 destination TEXT,
        #                 weight REAL
        #                 )
        #                 """)


# Add a ** new column ** to the shipments table
        # with connection: 
        #     #cursor.execute ("ALTER TABLE shipments ADD COLUMN status TEXT")
        #     cursor.execute("ALTER TABLE shipments ADD COLUMN content TEXT")


# POSTAPI ** Add values ** to the shipments table 
        # with connection:
        #     cursor.execute("""
        #         INSERT INTO shipments (id, origin, destination, weight, status, content)
        #                 VALUES(?,?,?,?,?,?)
        #                 """, (1731, 'seattle', 'new york', 18.57, 'placed', "electronics")
        #                 )


# GETAPI  ** fetch data ** from the shipments table using Select and only fecth used.
        # with connection: 
        #     cursor.execute("""
        #             SELECT id, status FROM shipments 
        #              WHERE status = ?""", ['placed'])# or (1730,)because it is a tuple
        #     row = cursor.fetchall()
        #     print(row)

    
    #   with connection: 
        # cursor.execute("""
        #          SELECT id, origin FROM shipments 
        #          WHERE id = 1730""")
        # result = cursor.fetchone()
        # print(result)

    # When to use fetchone() vs fetchall() and fetchmany()
        # - fetchone(): Use when you expect only one row of results.
        # - fetchall(): Use when you expect multiple rows of results and want to retrieve all of them at once.
        # - fetchmany(size): Use when you want to retrieve a specific number of rows at a time.


# patchAPI (Update) ** update data in the shipments table
        # with connection:
        #     cursor.execute ("UPDATE shipments SET status=? WHERE id= ?", ('placed', 1731))

# DELETEAPI ** delete data** from the shipments table
        # with connection:
        #     cursor.execute("DELETE FROM shipments WHERE id = ?", (1731,))

    # if i want alter like drop the from row 4 i ahve same data till 7 , but i want to kepp the data only in row 4, and rest from 5 i wnat to drop
        # with connection:
        #     cursor.execute("DELETE FROM shipments WHERE id > ?", (1734,)) 



# Work with the database using API endpoints 
            # class Database:
            #     def __init__ (self):
            #         self.db_path = Path("sqlite.db") 
            #         self.con = sqlite3.connect(self.db_path, check_same_thread=False) # connect to database file first
            #         self.con.row_factory = sqlite3.Row #For this connection, when I fetch rows, give me sqlite3.Row objects.
            #         self.cur = self.con.cursor() ## create cursor from that connection
            #         self.create_table("shipments")


            #     def create_table(self, table_name: str):
            #         with self.con:
            #             self.cur.execute( f"""
            #             CREATE TABLE if not exists {table_name} 
            #                 (
            #                 shipment_id INTEGER PRIMARY KEY, 
            #                 origin TEXT, 
            #                 destination TEXT,
            #                 content TEXT,
            #                 weight REAL,
            #                 shipment_status TEXT
            #                 )
            #                 """
            #                 )
                            # def create_shipment(self, shipment_id:int, shipment: Createshipment) ->Dict[str, Any]:
                            #     data = shipment.model_dump() # shipment.model_dump() gives a dictionary
                            #     with self.con:
                            #         self.cur.execute (""" 
                            #                           SELECT COALESCE(MAX(shipment_id), 1700) + 1 FROM shipments 
                            #                           """) # coalesce means use the first Not NULL value
                            #     data["shipment_id"] = self.cur.fetchone()[0] # get the first value from a tuple. because the result will be a tuple (1700,)
                            #     data["shipment_status"] = ShipmentStatus.PLACED.value # for dictionary we add value liek this : data["new_key"] = new_value
                            #            self.cur.execute("""
                            #                             INSERT INTO SHIPMENTS (
                            #                                 shipment_id, 
                            #                                 origin, 
                            #                                 destination,
                            #                                 content,
                            #                                 weight,
                            #                                 shipment_status
                            #                             )
                            #                             Values (
                            #                                 :shipment_id,
                            #                                 :origin,
                            #                                 :destination,
                            #                                 :content,
                            #                                 :weight,
                            #                                 :shipment_status
                            #                             )
                            #                             """, data)
                            #      return data
 
            # def create (self, shipment: Createshipment) -> Dict[str, Any]:
            #     data = shipment.model_dump()
            #     data["shipment_status"] = ShipmentStatus.PLACED.value
            #     with self.con:
            #         self.cur.execute("""
            #                          SELECT COALESCE(MAX(shipment_id), 1700) FROM shipments
            #                           """) #self.cur.execute(SQL_QUERY, VALUES_DICTIONARY)
            #         data["shipment_id"] = self.cur.fetchone()[0]+1
            #         columns = ",".join(data.keys())
            #         values = ",".join (f":{key}" for key in data.keys())
            #         self.cur.execute( f" INSERT INTO SHIPMENTS ({columns}) VALUES ({values}) ", data)
            #     return data
            
            # def get(self, shipment_id: int) -> dict[str, Any] | None:
            #     with self.con:
            #         self.cur.execute("""
            #                 select * from shipments 
            #                 where 
            #                         shipment_id = :shipment_id""",
            #                         {"shipment_id": shipment_id}
            #                         )

            #     row = self.cur.fetchone() # Now row is like a mix between a tuple and a dictionary.Because we set the row_factory to sqlite3.Row
            #     if row is None: 
            #         return None
            #     return dict(row) 
        
            # def update (self, shipment_id:int, shipment: Updateshipment) :
            #     with self.con: 
            #         self.cur.execute (""" 
            #                           UPDATE shipments 
            #                           SET shipment_status = :shipment_status
            #                           WHERE shipment_id = :shipment_id
            #                         """, 
            #                         {
            #                             "shipment_status": shipment.shipment_status, 
            #                             "shipment_id": shipment_id
            #                         }
            #                               )
            #     return self.get(shipment_id)
            
            # def delete (self, shipment_id: int )-> Dict[str, int]:
            #     with self.con:
            #         self.cur.execute("""
            #                          DELETE FROM shipments 
            #                          Where shipment_id= :shipment_id
            #                          """, 
            #                          {
            #                              "shipment_id": shipment_id
            #                          }
            #                          )
            #     return {"shipment_id": shipment_id}
    


            

            







    
    
        
# #In industry, database/business functions do not always return dictionaries. They may return:
# tuples
# dicts
# Pydantic models
# dataclasses
# ORM objects
# lists of any of those

# database.py
# : talks to SQLite and gets raw data.
# schemas.py
# : defines what valid input/output should look like.
# main.py
# : connects the API endpoint to the database and returns data in the shape the schema expects.

# ? vs :shipment_id is about how you SEND values into SQL.
# It is not about what you RETURN from SQL.

# 1. which direction your code depends on? idid you put this as a general way of saying that "pydantic models can be used for fats api end points and also can be used in the logic which is written in database.py module." or "Did you put that and wanted to say which is different perseption of telling me". 
# 2. if i use pydantic models at the end point it will become the validation and serailization  and if i use in the function it becomes the input varaible for the api, 
# 3. So if it cotains all the logic what suppose the api actaully does t

# if crashes: app starts
# -> db = Database() creates SQLite connection in one thread
# -> request comes in
# -> FastAPI runs your normal def endpoint in another worker thread
# -> db.get() tries to use the old SQLite connection/cursor
# -> SQLite refuses
# -> 500 error