import json
from pathlib import Path

from fastapi import HTTPException

from app.model.execution.response.LandCoverResponse import LandCoverResponse


DEMO_DIR = Path(__file__).resolve().parent.parent / "demo"
DEMO_DATA_FILE = DEMO_DIR / "demo_areas.json"


def get_demo_areas() -> list[LandCoverResponse]:
    if not DEMO_DATA_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Demo data not found",
        )

    try:
        with DEMO_DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return [
            LandCoverResponse.model_validate(item)
            for item in data
        ]

    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail="Invalid demo data",
        ) from exc


def get_demo_area(area_id: str) -> LandCoverResponse:
    for area in get_demo_areas():
        if area.id == area_id:
            return area

    raise HTTPException(
        status_code=404,
        detail="Area not found",
    )