from fastapi import FastAPI, HTTPException, status
from typing import Dict
from scalar_fastapi import get_scalar_api_reference
from  database import Database
from schemas import Createshipment, Updateshipment, Readshipment


app= FastAPI()
db= Database()

@app.post("/shipments", response_model = Updateshipment)
def create_shipment(shipment:Createshipment):
     return db.create(shipment)

@app.get("/shipments", response_model= Readshipment)
def get_shipment (shipment_id : int):
    shipment = db.get(shipment_id)
    if not shipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment_ID not found")
    return shipment

@app.patch("/shipments/{shipment_id}")
def update_shipment(shipment_id:int, shipment_status:Updateshipment) -> Dict[int, str] :
    shipment = db.get(shipment_id)
    if not shipment:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Shipment_ID not found")
    return db.update(shipment_id, shipment_status)

@app.delete("/shipments/{shipment_id}")
def delete_shipment(shipment_id: int):
    shipment = db.get(shipment_id)
    if not shipment:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Shipment_ID not found")
    return db.delete(shipment_id)

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="FastAPI Scalar Docs",
    )