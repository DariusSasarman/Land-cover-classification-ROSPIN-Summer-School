from typing import ClassVar, Dict, List
from app.model.execution.request.AOIRequest import AOIRequest

class AOIRequestRepo:
    _requests_by_id: ClassVar[Dict[str, AOIRequest]] = {}
    _ids_by_email: ClassVar[Dict[str, List[str]]] = {}

    @classmethod
    def save(cls, request_id: str, email: str, request: AOIRequest) -> AOIRequest:
        cls._requests_by_id[request_id] = request
        cls._ids_by_email.setdefault(email, []).append(request_id)
        return request

    @classmethod
    def list_for_email(cls, email: str) -> List[AOIRequest]:
        return [cls._requests_by_id[i] for i in cls._ids_by_email.get(email, [])]