import io
import json
import os
import time
import threading
from collections import deque
from typing import List, Tuple

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

from app.model.execution.response.History import HistoryItem
from app.logger import get_logger

load_dotenv()

logger = get_logger("service.InsightsService")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
GEMINI_RPM_LIMIT = int(os.getenv("GEMINI_RPM_LIMIT", "15"))


class _SlidingWindowRateLimiter:
    def __init__(self, max_calls: int, window_seconds: float = 60.0):
        self._max_calls = max_calls
        self._window = window_seconds
        self._calls = deque()
        self._lock = threading.Lock()

    def acquire(self):
        with self._lock:
            now = time.monotonic()
            while self._calls and now - self._calls[0] > self._window:
                self._calls.popleft()

            if len(self._calls) >= self._max_calls:
                wait_for = self._window - (now - self._calls[0])
                logger.info("Gemini RPM limit reached, waiting %.1fs...", wait_for)
                time.sleep(max(wait_for, 0))
                now = time.monotonic()
                while self._calls and now - self._calls[0] > self._window:
                    self._calls.popleft()

            self._calls.append(time.monotonic())


_rate_limiter = _SlidingWindowRateLimiter(max_calls=GEMINI_RPM_LIMIT)


def _pct_value(percentages: dict, class_id: str) -> float:
    raw = percentages.get(class_id, "0%")
    return float(str(raw).replace("%", "") or 0)


def _build_statistical_fallback(region: str, history: List[HistoryItem]) -> str:
    if not history:
        return "No classification history available yet."

    latest = history[-1].Classification.Percentages
    top_class, top_value = max(latest.items(), key=lambda item: float(item[1].replace("%", "")))

    vegetation = _pct_value(latest, "Forest") + _pct_value(latest, "HerbaceousVegetation")
    water = _pct_value(latest, "River") + _pct_value(latest, "SeaLake")

    lines = [
        f"- {region or 'This area'} shows **{top_class}** as the dominant land cover at {top_value}.",
        f"- Vegetation sits at {round(vegetation, 1)}% while water reaches {round(water, 1)}% in the latest acquisition.",
    ]

    if len(history) > 1:
        first_top_class = max(
            history[0].Classification.Percentages.items(),
            key=lambda item: float(item[1].replace("%", "")),
        )[0]
        if first_top_class != top_class:
            lines.append(f"- The dominant class shifted from **{first_top_class}** to **{top_class}** across the observed period.")
        else:
            lines.append(f"- **{top_class}** has remained the dominant class throughout the observed period.")

    return "\n".join(lines)


def _image_to_part(image: Image.Image):
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png")


def build_insights(
    region: str,
    history: List[HistoryItem],
    period_images: List[Tuple[str, Image.Image, Image.Image]] = None,
) -> str:
    if not history:
        return "No classification history available yet."

    fallback_stats = _build_statistical_fallback(region, history)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set, using statistical fallback insights")
        return fallback_stats

    try:
        client = genai.Client(api_key=api_key)

        history_data = [
            {
                "index": item.Classification.index,
                "period_desc": item.Classification.period_desc,
                "Percentages": item.Classification.Percentages,
            }
            for item in history
        ]

        contents = [
                f"""
            You are an expert geospatial and remote-sensing analyst generating a land-cover
            change report for {region or 'an unnamed area'}.

            Your job is NOT to produce generic observations about satellite imagery.
            Your job is to identify meaningful, evidence-based changes in the area over time
            and explain why those changes may matter to a property owner or land manager.

            You are given:

            1. A chronological history of land-cover classification percentages.
            2. RGB satellite images corresponding to periods in that history.

            The classification system contains these classes:

            - AnnualCrop
            - Forest
            - HerbaceousVegetation
            - Highway
            - Industrial
            - Pasture
            - PermanentCrop
            - Residential
            - River
            - SeaLake

            IMPORTANT EVIDENCE RULES:

            - Classification percentages are model predictions, not ground-truth measurements.
            - Never invent numerical values.
            - Never invent events, construction, development, agricultural activity,
            environmental damage, or other causes that are not supported by the evidence.
            - A change in classification does NOT automatically prove that real-world
            land-cover change occurred.
            - Do not describe a change as environmental degradation unless the evidence
            actually supports that interpretation.
            - Distinguish clearly between what is observed and what is inferred.
            - When evidence is insufficient, explicitly state the uncertainty.
            - Prefer persistent trends across multiple periods over isolated fluctuations.
            - Treat sudden one-period changes cautiously.
            - Consider classification error, seasonal variation, image quality, and
            acquisition differences when interpreting changes.
            - The model can sometimes confuse visually similar classes. In particular,
            apparent changes between River and Highway should be treated cautiously.

            NUMERICAL ANALYSIS:

            When comparing class percentages, use percentage-point differences.

            For example:
            53.7% → 65.3% = +11.6 percentage points.

            Do not describe this as an 11.6% increase.

            Prioritize:
            - large changes;
            - persistent changes;
            - abrupt changes;
            - changes involving important land-cover classes;
            - changes that are visually consistent with the RGB imagery.

            Do NOT waste report space describing every small numerical fluctuation.

            A useful insight should answer one or more of these questions:

            - What changed?
            - How large was the change?
            - When did it happen?
            - Was the change gradual or abrupt?
            - Did the change persist?
            - Is the change visible or spatially plausible in the imagery?
            - What are the most reasonable interpretations?
            - What should a property owner or land manager investigate next?

            STATISTICAL HISTORY:

            {json.dumps(history_data, indent=2)}

            REPORT STRUCTURE:

            # Land-Cover Change Report

            ## Executive Summary

            Write 2–4 sentences summarizing the most important findings.

            Mention:
            - the dominant land-cover pattern;
            - the most significant change;
            - whether the change appears persistent, gradual, or abrupt;
            - the practical significance, if supported by the evidence.

            Do not simply repeat the largest percentage.

            ## Key Findings

            Provide 3–5 concise bullet points.

            Each finding should contain, where applicable:
            - the class involved;
            - the time period;
            - the numerical change;
            - the direction of change;
            - why the change is noteworthy.

            Prioritize meaningful findings over completeness.

            ## Land-Cover Evolution

            Describe the important temporal patterns across the entire observation period.

            Identify:
            - persistent increases or decreases;
            - abrupt changes;
            - temporary fluctuations;
            - changes in the dominant land-cover class.

            Compare the earliest and latest observations when this provides useful context.

            Do not list every class unless it contributes to the interpretation.

            ## Visual Observations

            Use the RGB satellite imagery to support or challenge the statistical findings.

            Describe only patterns that are reasonably visible in the imagery.

            Do not claim exact boundaries, ownership, causes, or specific physical events
            unless they are directly supported by the provided evidence.

            ## Interpretation and Confidence

            For each major finding, distinguish between:

            **Observation:** What the classification data or imagery directly shows.

            **Interpretation:** What the observed pattern may indicate.

            **Confidence:** High, Medium, or Low.

            Use Low confidence when the interpretation could reasonably be explained by
            classification uncertainty, seasonal effects, image conditions, or limited
            temporal evidence.

            Do not present hypotheses as confirmed facts.

            ## Recommended Follow-Up

            Provide 1–3 practical follow-up actions only when justified by the findings.

            Examples:
            - inspect additional acquisition dates;
            - review higher-resolution imagery;
            - investigate a specific apparent land-cover transition;
            - validate a suspicious classification;
            - continue monitoring a persistent trend.

            Do not recommend actions merely to fill the section.

            STYLE:

            - Write clear, professional Markdown.
            - Be concise and information-dense.
            - Write for an intelligent non-specialist.
            - Use specific numbers and dates whenever useful.
            - Prefer "Industrial cover increased by 11.6 percentage points" over
            "Industrial cover increased significantly."
            - Avoid generic filler such as:
            "This highlights the importance of monitoring."
            "The area shows interesting dynamics."
            "These findings provide valuable insights."
            - Do not repeat the same observation in multiple sections.
            - Do not sensationalize changes.
            - Do not assume that every change is negative.
            - Do not force a conclusion when the evidence is ambiguous.

            FINAL QUALITY CHECK:

            Before producing the report, verify that:

            1. Every numerical claim is supported by the supplied statistics.
            2. Every visual claim is supported by the supplied imagery.
            3. Major changes are quantified where possible.
            4. Observations are separated from interpretations.
            5. Uncertain conclusions are explicitly marked as uncertain.
            6. No causes or events have been fabricated.
            7. The report contains actual insights rather than a restatement of the data.

            Return ONLY the Markdown report.
            """
            ]

        for period_desc, rgb_image, _mask_image in (period_images or []):
            contents.append(f"--- Period: {period_desc} (RGB View) ---")
            contents.append(_image_to_part(rgb_image))

        contents.append(
            f"Analyze this timeline sequence for {region or 'the area'}. "
            "Validate or expand upon the pre-extracted insights. "
            "Detail environmental degradation, growth spikes, or major shifts visible "
            "across the mask and RGB layers. Provide a concise executive report."
        )

        _rate_limiter.acquire()

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
        )

        if not response.text:
            logger.warning("Gemini returned empty response, using statistical fallback")
            return fallback_stats

        return response.text

    except Exception as exc:
        logger.error("Gemini insights generation failed: %s, using statistical fallback", exc)
        return fallback_stats