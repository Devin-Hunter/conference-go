import json
from django.http import JsonResponse
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods

from .models import Conference, Location, State
from .acls import get_photo, get_weather

class LocationListEncoder(ModelEncoder):
    model = Location
    properties = ["name"]

class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
        "state",
        "photo",
    ]

    def get_extra_data(self, o):
        return { "state": o.state.abbreviation }

class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
        "location",
    ]
    encoders = {
        "location": LocationListEncoder(),
    }

class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = ["name"]

@require_http_methods(["GET", "POST"])
def api_list_conferences(request):
    """
    Lists the conference names and the link to the conference.

    Returns a dictionary with a single key "conferences" which
    is a list of conference names and URLS. Each entry in the list
    is a dictionary that contains the name of the conference and
    the link to the conference's information.

    {
        "conferences": [
            {
                "name": conference's name,
                "href": URL to the conference,
            },
            ...
        ]
    }
    """
    if request.method == "GET":
        conferences = Conference.objects.all()
        return JsonResponse(
            {"conferences": conferences},
            encoder=ConferenceListEncoder,
        )
    else:
        content = json.loads(request.body)

        try:
            location = Location.objects.get(id=content["location"])
            content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid Location ID"},
                status=400,
            )
        conference = Conference.objects.create(**content)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False,
        )

    # response = []
    # conferences = Conference.objects.all()
    # for conference in conferences:
    #     response.append(
    #         {
    #             "name": conference.name,
    #             "href": conference.get_api_url(),
    #         }
    #     )
    # return JsonResponse({"conferences": response})

@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_conference(request, id):
    """
    Returns the details for the Conference model specified
    by the id parameter.

    This should return a dictionary with the name, starts,
    ends, description, created, updated, max_presentations,
    max_attendees, and a dictionary for the location containing
    its name and href.

    {
        "name": the conference's name,
        "starts": the date/time when the conference starts,
        "ends": the date/time when the conference ends,
        "description": the description of the conference,
        "created": the date/time when the record was created,
        "updated": the date/time when the record was updated,
        "max_presentations": the maximum number of presentations,
        "max_attendees": the maximum number of attendees,
        "location": {
            "name": the name of the location,
            "href": the URL for the location,
        }
    }
    """
    if request.method == "GET":
        conference = Conference.objects.get(id=id)

        # Use the city and state abbreviation of the Conference's Location
        # to call the get_weather_data ACL function and get back a dictionary
        # that contains the weather data

        city = conference.location.city
        state = conference.location.state
        show_weather = get_weather(city, state)
        # weather = {
        #     "weather_temp": show_weather["weather_temp"],
        #     "weather_description": show_weather["weather_description"]
        # }

        return JsonResponse(
            {"conference": conference,
            "show_weather": show_weather},
            encoder=ConferenceDetailEncoder,
            safe=False
        )
    elif request.method == "DELETE":
        count, _ = Conference.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            if "location" in content:
                location = Location.objects.get(id=content["location"])
                content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid Location ID"},
                status=400,
            )
        Conference.objects.filter(id=id).update(**content)
        conference = Conference.objects.get(id=id)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False,
        )

    # conference = Conference.objects.get(id=id)
    # return JsonResponse(
    #     {
    #         "name": conference.name,
    #         "starts": conference.starts,
    #         "ends": conference.ends,
    #         "description": conference.description,
    #         "created": conference.created,
    #         "updated": conference.updated,
    #         "max_presentations": conference.max_presentations,
    #         "max_attendees": conference.max_attendees,
    #         "location": {
    #             "name": conference.location.name,
    #             "href": conference.location.get_api_url(),
    #         },
    #     }
    # )

@require_http_methods(["GET", "POST"])
def api_list_locations(request):
    """
    Lists the location names and the link to the location.

    Returns a dictionary with a single key "locations" which
    is a list of location names and URLS. Each entry in the list
    is a dictionary that contains the name of the location and
    the link to the location's information.

    {
        "locations": [
            {
                "name": location's name,
                "href": URL to the location,
            },
            ...
        ]
    }
    """
    if request.method == "GET":
        location = Location.objects.all()
        return JsonResponse(
            {"location": location},
            encoder=LocationListEncoder
        )
    else:
        content = json.loads(request.body)

        try:
            state = State.objects.get(abbreviation=content["state"])
            content["state"] = state

        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )

        #Get picture URL from Pexels API
        state_full_name = state.name
        photo = get_photo(f'{content["city"]} {state_full_name}')
        content["photo"] = photo


        location = Location.objects.create(**content)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )

    # locations = [
    #     {
    #         "name": local.name,
    #         "href": local.get_api_url(),
    #     }
    #     for local in Location.objects.all()
    # ]
    # return JsonResponse({"locations": locations})

@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_location(request, id):
    """
    Returns the details for the Location model specified
    by the id parameter.

    This should return a dictionary with the name, city,
    room count, created, updated, and state abbreviation.

    {
        "name": location's name,
        "city": location's city,
        "room_count": the number of rooms available,
        "created": the date/time when the record was created,
        "updated": the date/time when the record was updated,
        "state": the two-letter abbreviation for the state,
    }
    """
    if request.method == "GET":
        location = Location.objects.get(id=id)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False
        )
    elif request.method == "DELETE":
        count, _ = Location.objects.filter(id=id).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            if "state" in content:
                state = State.objects.get(abbreviation=content["state"])
                content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )
        Location.objects.filter(id=id).update(**content)
        location = Location.objects.get(id=id)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )

    # location = Location.objects.get(id=id)
    # return JsonResponse(
    #     {
    #         "name": location.name,
    #         "city": location.city,
    #         "room_count": location.room_count,
    #         "created": location.created,
    #         "state": location.state.abbreviation
    #     }
    # )
