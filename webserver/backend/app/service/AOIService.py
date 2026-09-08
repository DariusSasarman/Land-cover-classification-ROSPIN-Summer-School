import uuid

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


def get_user_AOI_list(user_jwt: str):
    email = decode_jwt(user_jwt)["sub"]
    return AOIClassificationRepo.list_for_email(email)


def create_user_AOI(user_jwt: str, payload: AOIRequest) -> LandCoverResponse:
    email = decode_jwt(user_jwt)["sub"]
    request_id = str(uuid.uuid4())

    AOIRequestRepo.save(request_id, email, payload)

    periods = build_periods(
        payload.monitoring.frequency,
        payload.monitoring.startDate,
        payload.monitoring.endDate,
    )

    history = [
        HistoryItem(Classification=classify_area(
            area_id=request_id,
            period_id=period.period_id,
            period_desc=period.period_desc,
            period_index=period.index,
            area=payload.area,
            time_from=period.time_from,
            time_to=period.time_to,
        ))
        for period in periods
    ]

    result = LandCoverResponse(
        id=build_display_id(payload.requester.region, request_id),
        title=payload.requester.region or "Requested AOI",
        insights=build_insights(payload.requester.region, history),
        History=history,
    )

    AOIClassificationRepo.save(request_id, email, result)
    return result