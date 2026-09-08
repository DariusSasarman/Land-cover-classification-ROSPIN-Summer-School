import datetime
from typing import List, NamedTuple

FREQUENCY_MONTHS = {"monthly": 1, "quarterly": 3, "annual": 12}


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
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                       31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return datetime.date(year, month, day)


def _describe(period_start: datetime.date, frequency: str) -> str:
    if frequency == "monthly":
        return period_start.strftime("%b %Y").lower()
    if frequency == "quarterly":
        quarter = (period_start.month - 1) // 3 + 1
        return f"q{quarter} {period_start.year}"
    return str(period_start.year)


def build_periods(frequency: str, start_date: str | None, end_date: str | None) -> List[Period]:
    step_months = FREQUENCY_MONTHS.get(frequency, 3)

    if start_date and end_date:
        start = datetime.date.fromisoformat(start_date)
        end = datetime.date.fromisoformat(end_date)
    else:
        end = datetime.date.today()
        start = _add_months(end, -step_months)

    periods: List[Period] = []
    cursor = start
    index = 1

    while cursor < end:
        period_end = min(_add_months(cursor, step_months), end)

        periods.append(Period(
            index=str(index).zfill(2),
            period_id=cursor.isoformat(),
            period_desc=_describe(cursor, frequency),
            time_from=f"{cursor.isoformat()}T00:00:00Z",
            time_to=f"{period_end.isoformat()}T23:59:59Z",
        ))

        cursor = period_end
        index += 1

    return periods or [Period(
        index="01",
        period_id=start.isoformat(),
        period_desc=_describe(start, frequency),
        time_from=f"{start.isoformat()}T00:00:00Z",
        time_to=f"{end.isoformat()}T23:59:59Z",
    )]