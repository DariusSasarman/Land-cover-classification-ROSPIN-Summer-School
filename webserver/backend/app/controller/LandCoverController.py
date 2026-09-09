from fastapi import APIRouter, Header, BackgroundTasks

from app.service.DemoService import get_demo_areas, get_demo_area
from app.service.AOIService import (
    create_user_AOI,
    create_pending_AOI,
    get_user_AOI_list,
)
from app.model.execution.request.AOIRequest import AOIRequest
from app.logger import get_logger


logger = get_logger("controller.LandCoverController")

router = APIRouter(
    prefix="/api/land-cover",
    tags=["land-cover"],
)


@router.get("/list")
def list_aois(
    authorization: str = Header(...),
):
    logger.info(
        "Endpoint GET /api/land-cover/list invoked"
    )

    return get_user_AOI_list(
        authorization.removeprefix("Bearer ")
    )


@router.post("/createaoi")
def create_aoi(
    payload: AOIRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Header(...),
):
    logger.info(
        "Endpoint POST /api/land-cover/createaoi invoked "
        "for region '%s'",
        payload.requester.region,
    )

    user_jwt = authorization.removeprefix("Bearer ")

    request_id, pending_response = create_pending_AOI(
        user_jwt,
        payload,
    )

    background_tasks.add_task(
        create_user_AOI,
        request_id,
        user_jwt,
    )

    return pending_response


@router.get("/demo")
def list_demo_areas():
    logger.info(
        "Endpoint GET /api/land-cover/demo invoked"
    )

    return get_demo_areas()


@router.get("/demo/{area_id}")
def get_demo_area_endpoint(area_id: str):
    logger.info(
        "Endpoint GET /api/land-cover/demo/%s invoked",
        area_id,
    )

    return get_demo_area(area_id)


@router.get("/{area_id}")
def get_area(area_id: str):
    logger.info(
        "Endpoint GET /api/land-cover/%s invoked",
        area_id,
    )

    # Keep this endpoint for normal/user AOI handling.
    # Replace this with your existing AOI lookup if needed.
    return get_demo_area(area_id)