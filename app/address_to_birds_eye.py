import requests
import os
import shutil
import math

MAPQUEST_ENDPOINT = "http://open.mapquestapi.com/geocoding/v1/address"  # For geocoding
MAPBOX_ENDPOINT = "https://api.mapbox.com/v4/mapbox.satellite"
MAPBOX_ZOOM = 18
IMAGES_DIR = "images/"

MAPQUEST_API_KEY = os.getenv("MAPQUEST_KEY")
MAPBOX_API_KEY = os.getenv("MAPBOX_KEY")

# Use MapQuest to convert an address to a lat,long tuple
def address_to_lat_long(address):
    try:
        params = {'key': MAPQUEST_API_KEY, 'location': address}
        response = requests.get(MAPQUEST_ENDPOINT, params=params)
        response_json = response.json()
        status_code = response_json["info"]["statuscode"]
        if status_code != 0:
            return None, None
        latlong = response_json["results"][0]["locations"][0]["latLng"]
        return latlong["lat"], latlong["lng"]
    except Exception as e:
        print(e)
        return None, None


# Code from https://gis.stackexchange.com/questions/341330/get-zoomed-in-images-with-the-earthexplorer-api
# Get the y tile value based on a latitude value
def latToTile(latDeg, zoom):
    latRadians = math.radians(latDeg)
    n = 2.0 ** zoom
    return int((1.0 - math.asinh(math.tan(latRadians)) / math.pi) / 2.0 * n)


# Code from https://gis.stackexchange.com/questions/341330/get-zoomed-in-images-with-the-earthexplorer-api
# Get the x tile value based on a longitude value
def lonToTile(lonDeg, zoom):
    n = 2.0 ** zoom
    return int((lonDeg + 180.0) / 360.0 * n)


# Use MapBox to convert a lat,long pair into a satellite image
def lat_long_to_satellite_image(lat, long):
    url = (MAPBOX_ENDPOINT + "/" + str(MAPBOX_ZOOM) + "/" + str(lonToTile(long, MAPBOX_ZOOM)) +
           "/" + str(latToTile(lat, MAPBOX_ZOOM)) + "@2x.png?access_token=" + MAPBOX_API_KEY)

    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print("Error making get request to MapBox")
        return None
    name = "image-" + str(lat) + "-" + str(long) + ".png"
    image_path = IMAGES_DIR + name
    with open(image_path, "wb") as image:
        shutil.copyfileobj(response.raw, image)
        return image_path


def address_to_birds_eye(address):
    if address is None or len(address) < 1:
        raise Exception("No address provided")
    lat, long = address_to_lat_long(address)
    if lat is None or long is None:
        print("Error: could not get latlong")
        raise Exception("Failed to get latitude and longitude of the provided address. Please try another address")
    image_path = lat_long_to_satellite_image(lat, long)
    if image_path is None:
        print("Error: could not get image")
        raise Exception("Got latitude and longitude, but failed to get image of the provided address")
    return image_path
