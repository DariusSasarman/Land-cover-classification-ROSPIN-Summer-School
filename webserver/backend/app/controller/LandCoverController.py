from fastapi import APIRouter, HTTPException, Header
from app.service.DemoService import get_demo_areas
from app.service.AOIService import create_user_AOI, get_user_AOI_list
from app.model.execution.request.AOIRequest import AOIRequest

router = APIRouter(prefix="/api/land-cover", tags=["land-cover"])

@router.get("/list")
def list_aois(authorization: str = Header(...)):
    return get_user_AOI_list(authorization.removeprefix("Bearer "))

@router.post("/createaoi")
def create_aoi(payload: AOIRequest, authorization: str = Header(...)):
    return create_user_AOI(authorization.removeprefix("Bearer "), payload)

@router.get("/demo")
def list_demo_areas():
    return get_demo_areas()

@router.get("/{area_id}")
def get_demo_area(area_id: str):
    match = next((a for a in get_demo_areas() if a.id == area_id), None)
    if not match:
        raise HTTPException(404, "Area not found")
    return match