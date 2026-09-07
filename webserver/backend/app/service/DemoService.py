from app.model.execution.response.LandCoverResponse import LandCoverResponse
from app.model.execution.response.History import HistoryItem
from app.model.execution.response.Classification import Classification


_DEMO_RESPONSES = [
    LandCoverResponse(
        id="po-valley",
        title="Emilia-Romagna, Italy",
        insights=[
            "Emilia-Romagna remains the key reference area for Po Valley.",
            "Annual Crop leads the latest acquisition at 61.2%.",
            "Vegetation sits at 14.8% while water reaches 3.1% in the current archive.",
        ],
        History=[
            HistoryItem(Classification=Classification(
                index="01",
                period_desc="q3 2022",
                Percentages={
                    "Annual Crop": "54.8%", "Forest": "10.2%", "Pasture": "13.4%",
                    "River": "2.7%", "Sea / Lake": "1.8%", "HerbaceousVegetation": "17.1%",
                },
                RGB_IMAGE="https://picsum.photos/seed/po-valley-2022-Q3-rgb/960/640",
                Masked_IMAGE="https://picsum.photos/seed/po-valley-2022-Q3-mask/960/640?grayscale&blur=1",
            )),
            HistoryItem(Classification=Classification(
                index="02",
                period_desc="q4 2022",
                Percentages={
                    "Annual Crop": "56.1%", "Forest": "10.8%", "Pasture": "12.8%",
                    "River": "2.9%", "Sea / Lake": "2.0%", "HerbaceousVegetation": "15.4%",
                },
                RGB_IMAGE="https://picsum.photos/seed/po-valley-2022-Q4-rgb/960/640",
                Masked_IMAGE="https://picsum.photos/seed/po-valley-2022-Q4-mask/960/640?grayscale&blur=1",
            )),
        ],
    ),
    LandCoverResponse(
        id="black-forest",
        title="Baden-Württemberg, Germany",
        insights=[
            "Baden-Württemberg remains the key reference area for Black Forest.",
            "Forest leads the latest acquisition at 72.4%.",
            "Vegetation sits at 81.9% while water reaches 0.4% in the current archive.",
        ],
        History=[
            HistoryItem(Classification=Classification(
                index="01",
                period_desc="q3 2022",
                Percentages={
                    "Forest": "69.2%", "HerbaceousVegetation": "10.1%", "Pasture": "7.4%",
                    "Annual Crop": "4.8%", "Sea / Lake": "0.3%", "Residential": "8.2%",
                },
                RGB_IMAGE="https://picsum.photos/seed/black-forest-2022-Q3-rgb/960/640",
                Masked_IMAGE="https://picsum.photos/seed/black-forest-2022-Q3-mask/960/640?grayscale&blur=1",
            )),
        ],
    ),
    LandCoverResponse(
        id="danube-delta",
        title="Tulcea, Romania",
        insights=[
            "Tulcea remains the key reference area for Danube Delta.",
            "River leads the latest acquisition at 44.6%.",
            "Vegetation sits at 22.3% while water reaches 61.0% in the current archive.",
        ],
        History=[
            HistoryItem(Classification=Classification(
                index="01",
                period_desc="q3 2022",
                Percentages={
                    "River": "39.1%", "Sea / Lake": "20.4%", "HerbaceousVegetation": "17.8%",
                    "Annual Crop": "9.2%", "Forest": "4.1%", "Wetland Vegetation": "9.4%",
                },
                RGB_IMAGE="https://picsum.photos/seed/danube-delta-2022-Q3-rgb/960/640",
                Masked_IMAGE="https://picsum.photos/seed/danube-delta-2022-Q3-mask/960/640?grayscale&blur=1",
            )),
        ],
    ),
]


def get_demo_areas():
    #stub function to return demo responses, in a real scenario this would fetch data from a database or an external API
    return _DEMO_RESPONSES