const REQUEST_ENDPOINT = '/api/land-cover'

/** Local stand-ins matching the exact intended API shape. */
const STUB_RESPONSES = {
  'po-valley': {
    title: 'Emilia-Romagna, Italy',
    insights: [
      'Emilia-Romagna remains the key reference area for Po Valley.',
      'Annual Crop leads the latest acquisition at 61.2%.',
      'Vegetation sits at 14.8% while water reaches 3.1% in the current archive.',
      'Agricultural coverage has remained consistently dominant throughout the observed period.',
      'Forest coverage shows a slight seasonal decline during the summer acquisitions.',
    ],
    History: [
      {
        Classification: {
          index: '01',
          'period desc': 'q3 2022',
          Percentages: {
            'Annual Crop': '54.8%',
            Forest: '10.2%',
            Pasture: '13.4%',
            River: '2.7%',
            'Sea / Lake': '1.8%',
            HerbaceousVegetation: '17.1%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/po-valley-2022-Q3-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/po-valley-2022-Q3-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '02',
          'period desc': 'q4 2022',
          Percentages: {
            'Annual Crop': '56.1%',
            Forest: '10.8%',
            Pasture: '12.8%',
            River: '2.9%',
            'Sea / Lake': '2.0%',
            'HerbaceousVegetation': '15.4%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/po-valley-2022-Q4-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/po-valley-2022-Q4-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '03',
          'period desc': 'q1 2023',
          Percentages: {
            'Annual Crop': '58.0%',
            Forest: '9.0%',
            Pasture: '12.0%',
            River: '3.0%',
            'Sea / Lake': '2.2%',
            'HerbaceousVegetation': '15.8%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/po-valley-2023-Q1-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/po-valley-2023-Q1-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '04',
          'period desc': 'q2 2023',
          Percentages: {
            'Annual Crop': '61.2%',
            Forest: '8.5%',
            Pasture: '11.0%',
            River: '3.1%',
            'Sea / Lake': '2.0%',
            'HerbaceousVegetation': '14.2%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/po-valley-2023-Q2-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/po-valley-2023-Q2-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '05',
          'period desc': 'q3 2023',
          Percentages: {
            'Annual Crop': '63.4%',
            Forest: '7.9%',
            Pasture: '10.2%',
            River: '2.8%',
            'Sea / Lake': '2.1%',
            'HerbaceousVegetation': '13.6%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/po-valley-2023-Q3-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/po-valley-2023-Q3-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '06',
          'period desc': 'q4 2023',
          Percentages: {
            'Annual Crop': '59.8%',
            Forest: '9.1%',
            Pasture: '11.8%',
            River: '3.3%',
            'Sea / Lake': '2.3%',
            'HerbaceousVegetation': '13.7%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/po-valley-2023-Q4-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/po-valley-2023-Q4-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '07',
          'period desc': 'q1 2024',
          Percentages: {
            'Annual Crop': '60.5%',
            Forest: '9.4%',
            Pasture: '11.5%',
            River: '3.0%',
            'Sea / Lake': '2.2%',
            'HerbaceousVegetation': '13.4%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/po-valley-2024-Q1-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/po-valley-2024-Q1-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '08',
          'period desc': 'q2 2024',
          Percentages: {
            'Annual Crop': '61.2%',
            Forest: '8.7%',
            Pasture: '11.2%',
            River: '3.1%',
            'Sea / Lake': '2.0%',
            'HerbaceousVegetation': '13.8%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/po-valley-2024-Q2-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/po-valley-2024-Q2-mask/960/640?grayscale&blur=1',
        },
      },
    ],
  },

  'black-forest': {
    title: 'Baden-Württemberg, Germany',
    insights: [
      'Baden-Württemberg remains the key reference area for Black Forest.',
      'Forest leads the latest acquisition at 72.4%.',
      'Vegetation sits at 81.9% while water reaches 0.4% in the current archive.',
      'Forest coverage remains highly stable across the observed acquisitions.',
      'Seasonal variation is primarily visible in herbaceous vegetation and pasture classes.',
    ],
    History: [
      {
        Classification: {
          index: '01',
          'period desc': 'q3 2022',
          Percentages: {
            Forest: '69.2%',
            HerbaceousVegetation: '10.1%',
            Pasture: '7.4%',
            'Annual Crop': '4.8%',
            'Sea / Lake': '0.3%',
            Residential: '8.2%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/black-forest-2022-Q3-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/black-forest-2022-Q3-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '02',
          'period desc': 'q4 2022',
          Percentages: {
            Forest: '70.1%',
            HerbaceousVegetation: '9.6%',
            Pasture: '7.0%',
            'Annual Crop': '4.6%',
            'Sea / Lake': '0.4%',
            Residential: '8.3%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/black-forest-2022-Q4-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/black-forest-2022-Q4-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '03',
          'period desc': 'q1 2023',
          Percentages: {
            Forest: '70.0%',
            HerbaceousVegetation: '9.0%',
            Pasture: '6.0%',
            'Annual Crop': '5.0%',
            'Sea / Lake': '0.3%',
            Residential: '9.7%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/black-forest-2023-Q1-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/black-forest-2023-Q1-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '04',
          'period desc': 'q2 2023',
          Percentages: {
            Forest: '72.4%',
            HerbaceousVegetation: '9.5%',
            Pasture: '5.5%',
            'Annual Crop': '4.2%',
            'Sea / Lake': '0.4%',
            Residential: '8.0%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/black-forest-2023-Q2-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/black-forest-2023-Q2-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '05',
          'period desc': 'q3 2023',
          Percentages: {
            Forest: '73.1%',
            HerbaceousVegetation: '10.2%',
            Pasture: '5.0%',
            'Annual Crop': '3.8%',
            'Sea / Lake': '0.5%',
            Residential: '7.4%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/black-forest-2023-Q3-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/black-forest-2023-Q3-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '06',
          'period desc': 'q4 2023',
          Percentages: {
            Forest: '72.0%',
            HerbaceousVegetation: '9.1%',
            Pasture: '6.2%',
            'Annual Crop': '4.4%',
            'Sea / Lake': '0.4%',
            Residential: '7.9%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/black-forest-2023-Q4-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/black-forest-2023-Q4-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '07',
          'period desc': 'q1 2024',
          Percentages: {
            Forest: '71.6%',
            HerbaceousVegetation: '9.8%',
            Pasture: '6.5%',
            'Annual Crop': '4.3%',
            'Sea / Lake': '0.4%',
            Residential: '7.4%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/black-forest-2024-Q1-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/black-forest-2024-Q1-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '08',
          'period desc': 'q2 2024',
          Percentages: {
            Forest: '72.4%',
            HerbaceousVegetation: '9.5%',
            Pasture: '5.5%',
            'Annual Crop': '4.2%',
            'Sea / Lake': '0.4%',
            Residential: '8.0%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/black-forest-2024-Q2-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/black-forest-2024-Q2-mask/960/640?grayscale&blur=1',
        },
      },
    ],
  },

  'danube-delta': {
    title: 'Tulcea, Romania',
    insights: [
      'Tulcea remains the key reference area for Danube Delta.',
      'River leads the latest acquisition at 44.6%.',
      'Vegetation sits at 22.3% while water reaches 61.0% in the current archive.',
      'Water-related classes dominate the area and fluctuate with seasonal conditions.',
      'Herbaceous vegetation expands during the spring and summer acquisitions.',
    ],
    History: [
      {
        Classification: {
          index: '01',
          'period desc': 'q3 2022',
          Percentages: {
            River: '39.1%',
            'Sea / Lake': '20.4%',
            HerbaceousVegetation: '17.8%',
            'Annual Crop': '9.2%',
            Forest: '4.1%',
            'Wetland Vegetation': '9.4%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/danube-delta-2022-Q3-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/danube-delta-2022-Q3-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '02',
          'period desc': 'q4 2022',
          Percentages: {
            River: '38.4%',
            'Sea / Lake': '21.2%',
            HerbaceousVegetation: '16.5%',
            'Annual Crop': '9.8%',
            Forest: '4.3%',
            'Wetland Vegetation': '9.8%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/danube-delta-2022-Q4-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/danube-delta-2022-Q4-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '03',
          'period desc': 'q1 2023',
          Percentages: {
            River: '40.0%',
            'Sea / Lake': '18.0%',
            HerbaceousVegetation: '15.0%',
            'Annual Crop': '11.0%',
            Forest: '4.0%',
            'Wetland Vegetation': '12.0%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/danube-delta-2023-Q1-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/danube-delta-2023-Q1-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '04',
          'period desc': 'q2 2023',
          Percentages: {
            River: '44.6%',
            'Sea / Lake': '16.4%',
            HerbaceousVegetation: '14.0%',
            'Annual Crop': '10.2%',
            Forest: '3.8%',
            'Wetland Vegetation': '11.0%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/danube-delta-2023-Q2-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/danube-delta-2023-Q2-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '05',
          'period desc': 'q3 2023',
          Percentages: {
            River: '46.2%',
            'Sea / Lake': '14.8%',
            HerbaceousVegetation: '15.7%',
            'Annual Crop': '9.6%',
            Forest: '3.4%',
            'Wetland Vegetation': '10.3%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/danube-delta-2023-Q3-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/danube-delta-2023-Q3-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '06',
          'period desc': 'q4 2023',
          Percentages: {
            River: '43.8%',
            'Sea / Lake': '17.2%',
            HerbaceousVegetation: '14.4%',
            'Annual Crop': '10.5%',
            Forest: '3.9%',
            'Wetland Vegetation': '10.2%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/danube-delta-2023-Q4-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/danube-delta-2023-Q4-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '07',
          'period desc': 'q1 2024',
          Percentages: {
            River: '42.1%',
            'Sea / Lake': '18.5%',
            HerbaceousVegetation: '16.1%',
            'Annual Crop': '9.9%',
            Forest: '3.7%',
            'Wetland Vegetation': '9.7%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/danube-delta-2024-Q1-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/danube-delta-2024-Q1-mask/960/640?grayscale&blur=1',
        },
      },
      {
        Classification: {
          index: '08',
          'period desc': 'q2 2024',
          Percentages: {
            River: '44.6%',
            'Sea / Lake': '16.4%',
            HerbaceousVegetation: '14.0%',
            'Annual Crop': '10.2%',
            Forest: '3.8%',
            'Wetland Vegetation': '11.0%',
          },
          RGB_IMAGE: 'https://picsum.photos/seed/danube-delta-2024-Q2-rgb/960/640',
          Masked_IMAGE: 'https://picsum.photos/seed/danube-delta-2024-Q2-mask/960/640?grayscale&blur=1',
        },
      },
    ],
  },
}

/**
 * Fetches the land-cover archive for a given area.
 * STUBBED: returns local example data early. Remove the early return
 * once the real backend endpoint is live.
 */
export async function getDemoAreaHistory({ areaId }) {
  const stub = STUB_RESPONSES[areaId]
  if (stub) return stub

  // --- real API call (unreachable until stub above is removed) ---
  const response = await fetch(`${REQUEST_ENDPOINT}/demo/${areaId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })

  if (!response.ok) {
    throw new Error(`Land cover request failed: ${response.status}`)
  }

  return response.json()
}

export async function fetchAoiList(jwt) {
  const response = await fetch(`${REQUEST_ENDPOINT}/list`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${jwt}`,
    },
  })

  if (!response.ok) {
    throw new Error(`AOI list request failed: ${response.status}`)
  }

  return response.json()
}

export async function submitAoiRequest(payload, token) {
  const response = await fetch(`${REQUEST_ENDPOINT}/createaoi`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error(`AOI request failed: ${response.status}`)
  }

  return response.json()
}

