# app/plugins/generator/api/endpoint1.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/endpoint1888", tags=["generator"])
def read_endpoint1():
    return {"message": "Endpoint 1 from Generator Plugin"}
