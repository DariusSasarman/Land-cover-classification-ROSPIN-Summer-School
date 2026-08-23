import ee

ee.Authenticate()

print("Please enter your Google Earth Engine canvas project ID. " \
"\nYou can find it at https://code.earthengine.google.com/ under 'Project' in the top right corner.")

#project_id = 'canvas-provider-505813-b6'
project_id = input("Project ID: ")

ee.Initialize(project=project_id)
print(ee.String('Earth Engine connected successfully').getInfo())

lat_min, lat_max = 46.743444, 46.800056
lon_min, lon_max = 23.530639, 23.706639

aoi = ee.Geometry.Rectangle([lon_min, lat_min, lon_max, lat_max])

collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(aoi)
    .filterDate('2025-06-01', '2025-08-31')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))

image = collection.median().clip(aoi)

task = ee.batch.Export.image.toDrive(
    image=image.select(['B2','B3','B4','B8','B11','B12']),
    description='sentinel2_aoi',
    folder='rospin_export',
    scale=10,
    region=aoi
)
task.start()

print(task.status())