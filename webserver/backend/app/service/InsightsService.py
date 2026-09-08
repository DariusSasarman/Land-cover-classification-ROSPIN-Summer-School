from typing import List

from app.model.execution.response.History import HistoryItem


def _pct_value(percentages: dict, class_id: str) -> float:
    raw = percentages.get(class_id, "0%")
    return float(str(raw).replace("%", "") or 0)


def build_insights(region: str, history: List[HistoryItem]) -> List[str]:
    if not history:
        return []

    latest = history[-1].Classification.Percentages
    top_class, top_value = max(latest.items(), key=lambda item: float(item[1].replace("%", "")))

    vegetation = _pct_value(latest, "Forest") + _pct_value(latest, "HerbaceousVegetation")
    water = _pct_value(latest, "River") + _pct_value(latest, "SeaLake")

    insights = [
        f"{region or 'This area'} shows {top_class} as the dominant land cover at {top_value}.",
        f"Vegetation sits at {round(vegetation, 1)}% while water reaches {round(water, 1)}% in the latest acquisition.",
    ]

    if len(history) > 1:
        first_top_class = max(
            history[0].Classification.Percentages.items(),
            key=lambda item: float(item[1].replace("%", "")),
        )[0]
        if first_top_class != top_class:
            insights.append(f"The dominant class shifted from {first_top_class} to {top_class} across the observed period.")
        else:
            insights.append(f"{top_class} has remained the dominant class throughout the observed period.")

    return insights