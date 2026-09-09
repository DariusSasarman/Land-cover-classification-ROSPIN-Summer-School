import datetime
from typing import List, NamedTuple

FREQUENCY_MONTHS = {
    "monthly": 1,
    "quarterly": 3,
    "annual": 12,
}

# How much flexibility Copernicus gets around each target date.
SEARCH_WINDOW_DAYS = 15


class Period(NamedTuple):
    index: str
    period_id: str
    period_desc: str
    time_from: str
    time_to: str


def _add_months(d: datetime.date, months: int) -> datetime.date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1

    day = min(
        d.day,
        [
            31,
            29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
            31,
            30,
            31,
            30,
            31,
            31,
            30,
            31,
            30,
            31,
        ][month - 1],
    )

    return datetime.date(year, month, day)


def _describe(period_start: datetime.date, frequency: str) -> str:
    if frequency == "monthly":
        return period_start.strftime("%b %Y").lower()

    if frequency == "quarterly":
        quarter = (period_start.month - 1) // 3 + 1
        return f"q{quarter} {period_start.year}"

    return str(period_start.year)


def build_periods(
    frequency: str,
    start_date: str | None,
    end_date: str | None,
) -> List[Period]:

    step_months = FREQUENCY_MONTHS.get(frequency, 3)

    if start_date:
        start = datetime.date.fromisoformat(start_date)
    else:
        start = datetime.date.today()

    if end_date:
        end = datetime.date.fromisoformat(end_date)
    else:
        end = start

    periods: List[Period] = []

    cursor = start
    index = 1

    while cursor <= end:
        # The date at which we want an image.
        target_date = cursor

        # Small search window around the target date.
        # The frequency does NOT determine this window.
        window_start = max(
            target_date - datetime.timedelta(days=SEARCH_WINDOW_DAYS),
            start,
        )

        window_end = min(
            target_date + datetime.timedelta(days=SEARCH_WINDOW_DAYS),
            end,
        )

        periods.append(
            Period(
                index=str(index).zfill(2),
                period_id=target_date.isoformat(),
                period_desc=_describe(target_date, frequency),
                time_from=f"{window_start.isoformat()}T00:00:00Z",
                time_to=f"{window_end.isoformat()}T23:59:59Z",
            )
        )

        # Frequency only controls the jump to the next requested photo.
        cursor = _add_months(cursor, step_months)
        index += 1

    return periods