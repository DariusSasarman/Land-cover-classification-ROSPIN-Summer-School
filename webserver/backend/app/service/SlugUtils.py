import re


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "area"


def build_display_id(region: str, request_id: str) -> str:
    base = slugify(region) if region else "aoi"
    suffix = request_id.split("-")[0]  # first uuid segment, short and unique enough
    return f"{base}-{suffix}"