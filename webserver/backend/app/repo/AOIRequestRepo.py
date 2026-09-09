from typing import List, Optional
from app.model.execution.request.AOIRequest import AOIRequest
from app.storage.db import get_db, init_db
from app.logger import get_logger

logger = get_logger("repo.AOIRequestRepo")


class AOIRequestRepo:
    @classmethod
    def save(cls, request_id: str, email: str, request: AOIRequest) -> AOIRequest:
        init_db()
        logger.info("Saving AOI request ID '%s' for email: %s", request_id, email)
        data_json = request.model_dump_json()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO aoi_requests (request_id, email, data)
                VALUES (?, ?, ?)
                ON CONFLICT(request_id) DO UPDATE SET
                    email=excluded.email,
                    data=excluded.data
                """,
                (request_id, email, data_json),
            )
        return request

    @classmethod
    def get_by_request_id(cls, request_id: str) -> Optional[AOIRequest]:
        init_db()
        logger.debug("Fetching AOI request by ID: %s", request_id)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT data FROM aoi_requests WHERE request_id = ?",
                (request_id,),
            )
            row = cursor.fetchone()
            if row is None:
                logger.warning("No AOI request found for ID: %s", request_id)
                return None
            return AOIRequest.model_validate_json(row["data"])

    @classmethod
    def list_for_email(cls, email: str) -> List[AOIRequest]:
        init_db()
        logger.debug("Listing AOI requests for email: %s", email)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT data FROM aoi_requests WHERE email = ? ORDER BY created_at ASC",
                (email,),
            )
            rows = cursor.fetchall()
            logger.debug("Found %d AOI requests for email: %s", len(rows), email)
            return [AOIRequest.model_validate_json(row["data"]) for row in rows]