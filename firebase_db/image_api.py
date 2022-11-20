import os
import hashlib

import requests
import pyrebase

from firebase_db import FIREBASE_CONFIG
from tools.image.compress import compress_img


class ImageAPI:
    def __init__(self):
        self.firebase = pyrebase.initialize_app(FIREBASE_CONFIG).storage()

    def upload_image(self, old_image) -> str:
        _, file_extension = os.path.splitext(old_image.filename)

        read_image = old_image.read()

        if not read_image:
            raise Exception

        file_hash = hashlib.sha512()
        file_hash.update(read_image)
        file_hash = file_hash.hexdigest()

        new_file_name = file_hash + file_extension

        image_status = requests.get(self.get_original_image_url(new_file_name))

        if image_status.status_code == 404:
            self.firebase.child(f'original/{new_file_name}').put(read_image)

            compress_img(old_image, new_file_name)
            self.firebase.child(f'compress/{new_file_name}').put(new_file_name)
            os.remove(new_file_name)

            return new_file_name

        elif image_status.status_code == 200:
            return new_file_name
        else:
            raise Exception

    def get_original_image_url(self, image_name):
        return self.firebase.child(f'original/{image_name}').get_url(None)
