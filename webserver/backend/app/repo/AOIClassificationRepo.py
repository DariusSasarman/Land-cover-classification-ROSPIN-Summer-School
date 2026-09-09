from typing import List
from app.model.execution.response.LandCoverResponse import LandCoverResponse
from app.storage.db import get_db, init_db
from app.logger import get_logger

logger = get_logger("repo.AOIClassificationRepo")


class AOIClassificationRepo:
    @classmethod
    def save(cls, request_id: str, email: str, response: LandCoverResponse) -> LandCoverResponse:
        init_db()
        logger.info("Saving AOI classification output for request ID '%s' (email: %s)", request_id, email)
        data_json = response.model_dump_json()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO aoi_classifications (request_id, email, status, data)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(request_id) DO UPDATE SET
                    email=excluded.email,
                    status=excluded.status,
                    data=excluded.data
                """,
                (request_id, email, response.status, data_json),
            )
        return response

    @classmethod
    def list_for_email(cls, email: str) -> List[LandCoverResponse]:
        init_db()
        logger.debug("Listing AOI classifications for email: %s", email)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT data FROM aoi_classifications WHERE email = ? ORDER BY created_at ASC",
                (email,),
            )
            rows = cursor.fetchall()
            logger.debug("Found %d AOI classifications for email: %s", len(rows), email)
            return [LandCoverResponse.model_validate_json(row["data"]) for row in rows]