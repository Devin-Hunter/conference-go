from django.db.models import QuerySet
from json import JSONEncoder
from datetime import datetime
from typing import Any

class DateEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        else:
            return super().default(o)

class QuerySetEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, QuerySet):
            return list(o)
        else:
            return super().default(o)

class ModelEncoder(DateEncoder, QuerySetEncoder, JSONEncoder):
    encoders = {}

    def default(self, o):
        #   if the object to decode is the same class as what's in the
        #   model property, then
        if isinstance(o, self.model):
        #     * create an empty dictionary that will hold the property names
        #       as keys and the property values as values
            d = {}
        #     * for each name in the properties list
            if hasattr(o, "get_api_url"):
                d["href"] = o.get_api_url()

            for prop in self.properties:
        #         * get the value of that property from the model instance
        #           given just the property name
                value = getattr(o, prop)
        #         * put it into the dictionary with that property name as
        #           the key
                if prop in self.encoders:
                    encoder = self.encoders[prop]
                    value = encoder.default(value)
                    #are we reassigning the value variable with this line????
                d[prop] = value
            d.update(self.get_extra_data(o))
        #     * return the dictionary
            return d
        else:
            return super().default(o)

    def get_extra_data(self, o):
        return {}
