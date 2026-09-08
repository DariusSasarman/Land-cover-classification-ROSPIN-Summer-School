from typing import ClassVar, Dict, List
from app.model.execution.response.LandCoverResponse import LandCoverResponse


class AOIClassificationRepo:
    _responses_by_id: ClassVar[Dict[str, LandCoverResponse]] = {}
    _ids_by_email: ClassVar[Dict[str, List[str]]] = {}

    @classmethod
    def save(cls, request_id: str, email: str, response: LandCoverResponse) -> LandCoverResponse:
        cls._responses_by_id[request_id] = response
        cls._ids_by_email.setdefault(email, []).append(request_id)
        return response

    @classmethod
    def list_for_email(cls, email: str) -> List[LandCoverResponse]:
        return [cls._responses_by_id[i] for i in cls._ids_by_email.get(email, [])]