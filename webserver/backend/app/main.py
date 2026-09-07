from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.controller.AuthController import router as auth_router
from app.controller.LandCoverController import router as land_cover_router
app = FastAPI()

app.include_router(land_cover_router)
app.include_router(auth_router)

app.mount("/", StaticFiles(directory="./app/static",html = True), name="static")
