import os
import time
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.logger import get_logger
from app.controller.AuthController import router as auth_router
from app.controller.LandCoverController import router as land_cover_router
from app.storage.db import init_db


logger = get_logger("main")


logger.info("Initializing database...")
init_db()


app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    method = request.method
    url_path = request.url.path

    logger.info(
        "HTTP %s %s - Client: %s",
        method,
        url_path,
        client_ip,
    )

    try:
        response = await call_next(request)

        elapsed_ms = round(
            (time.time() - start_time) * 1000,
            2,
        )

        logger.info(
            "HTTP %s %s Completed %d in %sms",
            method,
            url_path,
            response.status_code,
            elapsed_ms,
        )

        return response

    except Exception as exc:
        elapsed_ms = round(
            (time.time() - start_time) * 1000,
            2,
        )

        logger.error(
            "HTTP %s %s Failed after %sms: %s\n%s",
            method,
            url_path,
            elapsed_ms,
            exc,
            traceback.format_exc(),
        )

        raise


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.error(
        "Unhandled Exception on %s %s: %s\n%s",
        request.method,
        request.url.path,
        exc,
        traceback.format_exc(),
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error"
        },
    )


# API routers
app.include_router(land_cover_router)
app.include_router(auth_router)


# Normal AOI images
storage_images_dir = os.path.join(
    os.path.dirname(__file__),
    "storage",
    "images",
)

os.makedirs(
    storage_images_dir,
    exist_ok=True,
)

app.mount(
    "/images",
    StaticFiles(
        directory=storage_images_dir
    ),
    name="images",
)

logger.info(
    "Mounted static image directory: %s",
    storage_images_dir,
)


# Permanent demo images
demo_images_dir = os.path.join(
    os.path.dirname(__file__),
    "demo",
    "images",
)

os.makedirs(
    demo_images_dir,
    exist_ok=True,
)

app.mount(
    "/demo/images",
    StaticFiles(
        directory=demo_images_dir
    ),
    name="demo-images",
)

logger.info(
    "Mounted demo image directory: %s",
    demo_images_dir,
)


# React frontend
static_dir = os.path.join(
    os.path.dirname(__file__),
    "static",
)

app.mount(
    "/",
    StaticFiles(
        directory=static_dir,
        html=True,
    ),
    name="static",
)

logger.info(
    "Mounted static webapp directory: %s",
    static_dir,
)