import os
from uuid import uuid4
from functools import wraps


def uuid_upload_to(path):
    @wraps(uuid_upload_to)
    def uuid_filename(instance, filename):
        try:
            extension = filename.split('.')[-1]
        except IndexError:
            extension = ''
        return os.path.join(path, f'{str(uuid4())}.{extension}')

    return uuid_filename
