import os
from uuid import uuid4
from functools import wraps
from math import radians, sin, cos, sqrt, asin


def uuid_upload_to(path):
    @wraps(uuid_upload_to)
    def uuid_filename(instance, filename):
        try:
            extension = filename.split('.')[-1]
        except IndexError:
            extension = ''
        return os.path.join(path, f'{str(uuid4())}.{extension}')

    return uuid_filename


def calculate_distance(point_1, point_2):
    lat1, lon1 = radians(point_1[0]), radians(point_1[1])
    lat2, lon2 = radians(point_2[0]), radians(point_2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))

    r = 6371

    return c * r * 1000
