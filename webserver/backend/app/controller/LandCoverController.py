from fastapi import APIRouter, HTTPException, Header, BackgroundTasks
from app.service.DemoService import get_demo_areas
from app.service.AOIService import create_user_AOI, create_pending_AOI, get_user_AOI_list
from app.model.execution.request.AOIRequest import AOIRequest
from app.logger import get_logger

logger = get_logger("controller.LandCoverController")

router = APIRouter(prefix="/api/land-cover", tags=["land-cover"])


@router.get("/list")
def list_aois(authorization: str = Header(...)):
    logger.info("Endpoint GET /api/land-cover/list invoked")
    return get_user_AOI_list(authorization.removeprefix("Bearer "))


@router.post("/createaoi")
def create_aoi(
    payload: AOIRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Header(...),
):
    logger.info("Endpoint POST /api/land-cover/createaoi invoked for region '%s'", payload.requester.region)
    user_jwt = authorization.removeprefix("Bearer ")

    # Synchronously create a pending stub and store request payload in the DB
    request_id, pending_response = create_pending_AOI(user_jwt, payload)

    # Schedule the full classification pipeline to run in the background
    background_tasks.add_task(create_user_AOI, request_id, user_jwt)

    # Return the pending stub immediately so the front-end can display "Work in progress"
    return pending_response


@router.get("/demo")
def list_demo_areas():
    logger.info("Endpoint GET /api/land-cover/demo invoked")
    return get_demo_areas()


@router.get("/{area_id}")
def get_demo_area(area_id: str):
    logger.info("Endpoint GET /api/land-cover/%s invoked", area_id)
    match = next((a for a in get_demo_areas() if a.id == area_id), None)
    if not match:
        logger.warning("Demo area ID '%s' not found", area_id)
        raise HTTPException(404, "Area not found")
    return match

