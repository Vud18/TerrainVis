from fastapi import FastAPI
from app.api import router as app_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(app_router)
