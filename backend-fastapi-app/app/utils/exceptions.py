from fastapi import HTTPException, status

def raise_not_found_exception(entity: str):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity} not found")
