# app/routers/docs.py
from fastapi import APIRouter
from fastapi.responses import FileResponse
import json

router = APIRouter()

@router.get("/openapi.json", include_in_schema=False)
async def get_openapi_schema():
    schema = app.openapi()
    with open("openapi.json", "w") as f:
        json.dump(schema, f)
    return FileResponse("openapi.json")