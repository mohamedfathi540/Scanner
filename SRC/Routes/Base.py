from fastapi import FastAPI,APIRouter,Depends,Request
from fastapi.responses import JSONResponse
import os
from Helpers.Config import get_settings,settings

base_router = APIRouter(
    prefix = "/api/v1",
    tags = ["api_v1"]

)

@base_router.get("/")
async def welcome(app_settings : settings = Depends(get_settings)):

    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION

    return {
        "app_name" : app_name ,
        "app_version" : app_version
    }

@base_router.get("/prescription/shared/{token}")
async def get_shared_prescription(token: str, request: Request):
    return JSONResponse(status_code=404, content={"signal": "NOT_FOUND"})
