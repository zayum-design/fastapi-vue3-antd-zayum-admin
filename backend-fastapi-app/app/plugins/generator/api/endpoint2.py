# app/plugins/generator/api/endpoint2.py
from fastapi import APIRouter
from app.utils.log_utils import logger

router = APIRouter() 

@router.get("/endpoint2", tags=["generator"])
def read_endpoint2():
    logger.info("Endpoint2 accessed.")
    return {"message": "Endpoint 2 from Generator Plugin"}
