import uuid
from typing import Tuple

from app.Security import decode_jwt
from app.repo.AOIRequestRepo import AOIRequestRepo
from app.repo.AOIClassificationRepo import AOIClassificationRepo
from app.model.execution.request.AOIRequest import AOIRequest
from app.model.execution.response.LandCoverResponse import LandCoverResponse
from app.model.execution.response.History import HistoryItem
from app.service.ClassificationService import classify_area
from app.service.PeriodPlanner import build_periods
from app.service.InsightsService import build_insights
from app.service.SlugUtils import build_display_id
from app.logger import get_logger

logger = get_logger("service.AOIService")


def get_user_AOI_list(user_jwt: str):
    email = decode_jwt(user_jwt)["sub"]
    logger.info("Fetching AOI classification list for user: %s", email)
    return AOIClassificationRepo.list_for_email(email)


def create_pending_AOI(user_jwt: str, payload: AOIRequest) -> Tuple[str, LandCoverResponse]:
    """
    Synchronously creates and persists a pending (in_progress) LandCoverResponse stub,
    also persisting the AOIRequest payload so the background task can retrieve it.
    Returns (request_id, pending_response).
    """
    email = decode_jwt(user_jwt)["sub"]
    request_id = str(uuid.uuid4())
    logger.info("Creating pending AOI stub for user '%s', request ID: %s", email, request_id)

    AOIRequestRepo.save(request_id, email, payload)

    pending = LandCoverResponse(
        id=build_display_id(payload.requester.region, request_id),
        title=payload.requester.region or "Requested AOI",
        status="in_progress",
        insights=["Your area of interest is being processed. Please check back shortly."],
        History=[],
    )
    AOIClassificationRepo.save(request_id, email, pending)
    logger.info("Pending AOI stub saved for request ID: %s", request_id)
    return request_id, pending


def create_user_AOI(request_id: str, user_jwt: str) -> LandCoverResponse:
    """
    Background task: fetches the stored AOI request by ID, runs the full
    classification pipeline, and replaces the in_progress stub with the
    completed LandCoverResponse.
    """
    email = decode_jwt(user_jwt)["sub"]
    logger.info("Starting background AOI pipeline for user '%s', request ID: %s", email, request_id)

    try:
        payload = AOIRequestRepo.get_by_request_id(request_id)
        if payload is None:
            logger.error("Cannot run pipeline: no stored request found for ID '%s'", request_id)
            return

        periods = build_periods(
            payload.monitoring.frequency,
            payload.monitoring.startDate,
            payload.monitoring.endDate,
        )
        logger.info("Generated %d monitoring periods for request ID '%s'", len(periods), request_id)

        history = []
        for idx, period in enumerate(periods, start=1):
            logger.info(
                "Processing period %d/%d ('%s') for request ID '%s'...",
                idx, len(periods), period.period_desc, request_id,
            )
            classification = classify_area(
                area_id=request_id,
                period_id=period.period_id,
                period_desc=period.period_desc,
                period_index=period.index,
                area=payload.area,
                time_from=period.time_from,
                time_to=period.time_to,
            )
            history.append(HistoryItem(Classification=classification))

        result = LandCoverResponse(
            id=build_display_id(payload.requester.region, request_id),
            title=payload.requester.region or "Requested AOI",
            status="done",
            insights=build_insights(payload.requester.region, history),
            History=history,
        )

        AOIClassificationRepo.save(request_id, email, result)
        logger.info("Background AOI pipeline completed successfully for request ID '%s'", request_id)
        return result
    except Exception as exc:
        logger.error("Background AOI pipeline failed for request ID '%s' (email: %s): %s", request_id, email, exc)
        raise exc