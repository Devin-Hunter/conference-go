from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY
from .models import Conference
import requests
import json



def get_photo(query):
    """ Get the URL of a picture from the Pexels API."""
    url = f"https://api.pexels.com/v1/search?query={query}"

    headers = {"Authorization": PEXELS_API_KEY}

    response = requests.get(url, headers=headers)
    api_dict = response.json()
    return api_dict['photos'][0]['src']['original']



def get_weather(city, state):
    """Get the URL of the current weather for the location specified"""
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{state},US&limit=1&appid={OPEN_WEATHER_API_KEY}"
    geo_response = requests.get(url)
    dict = geo_response.json()
    geo = {
        "lat": dict[0]["lat"],
        "lon": dict[0]["lon"],
    }

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={geo['lat']}&lon={geo['lon']}&appid={OPEN_WEATHER_API_KEY}&units=imperial"
    weather_response = requests.get(url)
    weather_dict = weather_response.json()
    weather = {
        "weather_temp": weather_dict["main"]["temp"],
        "weather_description": weather_dict["weather"][0]["description"],
    }
    # print(weather['description'])
    # print(weather['temp'])
    return weather

    # ['description'], weather['temp']
