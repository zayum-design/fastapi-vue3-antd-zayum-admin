# plugins/sample-payment-plugin/backend/main.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/create")
async def create_payment():
    return {"status": "success"}


@router.get("/create")
async def create_payment():
    return {"status": "success"}




@router.post("/settings")
async def create_payment():
    return {"status": "success"}


@router.get("/settings")
async def create_payment():
    return {"status": "success"}