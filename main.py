#binal patel
#from typing import Any, Callable
#
#from httpx import request
#
#my_list: list[int] = [1, 2, 3, 4, 5]
#my_tuple: tuple[int, ...] = (1, 2, 3, 4, 5)
#my_dict: dict[str, Any] = {
#    "city": "New York",
#    "population": 8000000,
#    "country": "USA"
#}
#def root_square(num: int | float, exp: float | None=0.5):
#    return pow(num, exp)
#
#class city():
#    def __init__(self, name: str, population: int | float):
#        self.name = name
#        self.population = population
#        return None
#
#    def country(self, country: str):
#        self.country = country
#        return self.country
#    def __str__(self):        
#        return f"{self.name} is a city in {self.country} with a population of {self.population}"  
#new_york = city("New York", 8000000)
#new_york.country("USA")
#print(new_york)
#
#
#
#
#def timer(func):
#    def time_took_in_between():
#        print("Starting time-consuming task...")
#        func()
#        print("Finished time-consuming task.")
#        return time_took_in_between
#
#def cal_time_consuming():
#    print(" time-consuming task in process...")
#
#cal_time_consuming()
#
##--------------------------
##this is sample example in use of Decorators with parameters
#
#def custom_symbol(symbol: str = "!"):
#    def fence(func):
#        def wrapper(text : str):
#            print(symbol*len(text))
#            func(text)
#            print(symbol*len(text))
#        
#        return wrapper
#    return fence
#
#
#@custom_symbol("=")
#def log (text : str):
#  print (text)
#
#log("Hello from the log function!") # Pass a string argument
#
##---------------------------
##this is sample example in use of Decorators with callable type hinting
#from typing import Callable    # Mypy will recognize this as a type hint for a callable function
#
#route : dict[str, Callable[[Any], Any]] = {}
#
#def routes(path: str):
#    def registerd_routes(func):
#        route[path] = func
#        return func
#    return registerd_routes
#
#@routes("/shipment")
#def get_shipment():
#    return "This is the shipment route"
#
#request: str = ""  # noqa: F811
#while request != "exit":
#    request = input("Enter a route (or 'exit' to quit): ")
#    if request in route:
#        print(route[request]())
#    elif request != "exit":
#        print("Route not found. Please try again.")
#
#----------------------------
#Example For HTTPException, handling errors in FastAPI, in GET requests, POST requests
#from collections.abc import Callable  #only useful for type hinting callable functions  # not used
import json

from data import shipments, save
from fastapi import FastAPI, HTTPException, status 
from typing import Any, Union                 # used
from schemas import Createshipment, Readshipment, Updateshipment
from scalar_fastapi import get_scalar_api_reference   # used
#from fastapi.openapi.docs import get_swagger_ui_html  # not used


#from data import shipments, save # i need data to import because it contains the shipment data and the save function




app = FastAPI()

# shipments: dict[int, Any] = {
#     1730: {
#         "origin": "New York",
#         "destination": "Los Angeles",
#         "shipment_status": "In Transit",
#         "weight": 30,
#     },
#     1731: {
#         "origin": "Chicago",
#         "destination": "Houston",
#         "shipment_status": "Delivered",
#         "weight": 250,
#     },
#     1732: {
#         "origin": "San Francisco",
#         "destination": "Seattle",
#         "shipment_status": "Pending",
#         "weight": 500,
#     },
#     1733: {
#         "origin": "Miami",
#         "destination": "Atlanta",
#         "shipment_status": "In Transit",
#         "weight": 150,
#     },
#     1734: {
#         "origin": "Denver",
#         "destination": "Phoenix",
#         "shipment_status": "Delayed",
#         "weight": 320,
#     },
#     1735: {
#         "origin": "Boston",
#         "destination": "Philadelphia",
#         "shipment_status": "Delivered",
#         "weight": 200,
#     },
# }

#----------------------------
# @app.get("/shipments/latest")
# def get_latest_shipment() -> dict[str, Any]:
#     if not shipments:
#         raise HTTPException(status_code=404, detail="No shipments available")
#     latest_shipment_id = max(shipments.keys())
#     return shipments[latest_shipment_id]
#---------------------------------------------------------
# This is for getting a specific field from a shipment 
# For example, to get the origin of a shipment with ID 1730: 
# Small output example is: "New York"
# @app.get("/shipments/{shipment_id}/{field}")
# def get_shipment_by_field(shipment_id: int, field: str) -> Any:
#     if shipment_id not in shipments:
#         raise HTTPException(status_code=404, detail="Shipment not found")
#     if field not in shipments[shipment_id]:
#         raise HTTPException(status_code=404, detail="Field not found")
#     return shipments[shipment_id][field]
#--------------------------------------------------------------------
# This is for filtering shipments by a specific field and value
# For example, to get all shipments with status "Delivered":
# @app.get("/shipments/filter/{field}/{value}")
# def filter_shipments(field: str, value: str) -> dict[int, dict[str, Any]]:
#     filtered = {id: details for id, details in shipments.items() if str(details.get(field, "")).lower() == value.lower()}
#     if not filtered:
#         raise HTTPException(status_code=404, detail=f"No shipments found with {field}={value}")
#     return filtered
#--------------------------------------------------------------
@app.get("/shipments", response_model=Readshipment)
def get_shipment(shipment_id: int) :
    if shipment_id not in shipments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Shipment not found")
    return shipments[shipment_id]
    
@app.post("/shipments") #response_model=Createshipment)
def submit_shipment(shipment: Createshipment)  -> dict[str, int]:
    new_shipment_id = max(shipments.keys()) + 1    
    # IMP: we dont need to validate the weight here because it's already validated in the schema
    # shipments[new_shipment_id] = shipment.model_dump()
    shipments[new_shipment_id] = {

    **shipment.model_dump(mode="json"),

    "id": new_shipment_id,
    }
    
    #{
    #     "origin": origin,
    #     "destination": destination,
    #     "shipment_status": shipment_status,
    #     "weight": weight
    # }
    save()
    return {"shipment_id": new_shipment_id}
    #return shipments[new_shipment_id]

@app.patch("/shipments", response_model=Readshipment)
def update_shipment(shipment_id: int, shipment: Updateshipment): # -> dict[str, Any]:
    if shipment_id not in shipments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")
    #shipments[shipment_id].update(shipment.dict(exclude_unset=True)) 
    update_status= shipment.model_dump(exclude_none=True, mode = "json") #here exclude_unset or exclude_none=True means that we will only update the fields that are explicitly set in the request. here shipment.model_dump() means to convert the Pydantic model to a dictionary.
    shipments[shipment_id].update(update_status)
    save()
    return shipments[shipment_id]

@app.delete("/shipments/{shipment_id}")
def delete_shipment(shipment_id: int):
    if shipment_id not in shipments:
        raise HTTPException(status_code=status.HTTP_222_UNPROCESSABLE_ENTITY, detail="Shipment not found")
    else:
        deleted_shipment = shipments.pop(shipment_id)
        save()
        #return {"message": f"Shipment {shipment_id} deleted successfully", "shipment_id": shipment_id}
        return {"message": "Shipment {} deleted successfully".format(deleted_shipment)}

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="FastAPI Scalar Docs",
    )

# @app.post("/shipments")
# #def post_shipment(origin: str, destination: str,  weight: Union[int, float], shipment_status: str) -> dict[str, int]:
# def post_shipment(weight: Union[int, float], data: dict[str,Any]) -> dict[str, Any]:
#     origin = data["origin"]
#     destination = data["destination"]   
#     shipment_status = data["shipment_status"]
#     new_id = max(shipments.keys()) + 1 if shipments else 1
#     if weight <= 0:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Weight should be greater than zero"
#         )
#     if weight > 25:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Maximum weight limit is 25 kg"
#         )
#     shipments[new_id] = {
#         "origin": origin,
#         "destination": destination,
#         "shipment_status": shipment_status,
#         "weight": weight
#     }
#     return {"shipment_id": new_id}

# @app.patch("/shipments/{shipment_id}")
# def update_shipment(shipment_id: int, data: dict[str, Union[str, float, int]])-> dict[str, Union[str, float, int]]:
#     if shipment_id not in shipments:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found")
#     shipments[shipment_id].update(data)
#     return shipments[shipment_id]

#  @app.get ("/shipments/status/{status}")
#  def get_shipments_by_status(status: str):
#     filtered_shipments = {id: details for id, details in shipments.items() if details["status"].lower() == status.lower()}
#      return filtered_shipments
#/Users/durgathulluru/Documents/python study material/python Project_API/app
#Logical Flow of API Request: 
# 1. Client sends a request to the  API endpoint and fast api will address the right api function handler
# 2. The API checks if the shipment exists.
# 3. If the shipment exists, it is deleted from the data store.
# 4. A success message is returned to the client. 


# @app.get("/shipments/{id}")
# def get_shipment(id: int) -> dict[str, Any]:
#     if id not in shipments:
#         raise HTTPException(stataus_code = status.HTTP_222_UNPROCESSABLE_ENTITY, details = "shipment id is not valid, try again")
#         return shipments[id]
# @app.post("/shipments")
# def post_shipment(data: dict[str, str|int|float]) -> data[str, str ]: 
#     origin =data["origin"]
#     destination = data["destination"]
#     weight = data ["weight"]
#     status = data["status"]

#     new_shipment_id = max (shipments.keys()) + 1
#     shipments[new_shipment_id] = {
#         "origin": origin,
#         "destination": destination,
#         "shipment_status": status,
#         "weight": weight
#     }
#     return {"shipment_id": new_shipment_id}
# post
# @app.post("/shipments")
# def post_shipment (origin: str, destination: str, weight: int, status: str) -> dict[str, int]:
#     new_id = max(shipments.keys()) + 1
#     if weight <= 0:
#         raise HTTPException(status_code= status.HTTP_400_NOT_ACCEPTABLE, detail="Weight should not be zero")
#     if weight > 25:
#         raise HTTPException(
#             status_code= status.HTTP_400_NOT_ACCEPTABLE, 
#             detail="MAXIMUM Weight is 25")
#     shipments[new_id] = {
#         "origin" : origin,
#         "destination" : destination,
#         "status" : status,
#         "weight" : weight
#     }
#     return {"shipment_id": new_id}