import datetime
from collections import OrderedDict

import pyrebase

from firebase_db import FIREBASE_CONFIG
from users_db.user_api import get_user_info_by_id
from firebase_db.image_api import ImageAPI


image_api = ImageAPI()


class MessageAPI:
    def __init__(self):
        self.firebase = pyrebase.initialize_app(FIREBASE_CONFIG).database()

    def create_message(self,
                       user_id: int,
                       post_date: int = int(datetime.datetime.utcnow().timestamp()),
                       message_text: str = None,
                       image_hash_name: str = None,
                       private_user_id: int = 'Public'):
        data = {
            'datetime': post_date,
            'message': message_text,
            'image_hash_name': image_hash_name
        }
        self.firebase.child('Message').child(user_id).child(private_user_id).push(data)

    def read_all_user_public_messages(self, user_id: int) -> dict:
        return self.firebase.child('Message').child(user_id).child('Public').get().val()

    def read_all_public_messages(self) -> dict:
        all_messages = self.firebase.child('Message').get().val()

        if not all_messages:
            self.create_message(1, message_text='hello word')
            all_messages = self.firebase.child('Message').get().val()

        all_public_messages = OrderedDict()

        for user_id in range(len(all_messages)):
            msgs = all_messages[user_id]
            if msgs and msgs.get('Public'):
                for msg_id in msgs['Public']:
                    all_public_messages[msg_id] = {
                        'user': {'user': user_id, 'username': get_user_info_by_id(user_id).login},
                        **msgs['Public'][msg_id]
                    }

        return all_public_messages

    def read_all_public_messages2(self, first_message=None, last_message=None):
        all_messages = self.firebase.child('Message').get().val()
        all_public_messages = []

        if not all_messages:
            self.create_message(1, message_text='hello word')
            all_messages = self.firebase.child('Message').get().val()

        for index in range(len(all_messages)):
            all_public_user_messages = all_messages[index]
            if all_public_user_messages:
                for message_id in all_public_user_messages['Public']:
                    this_massage = all_public_user_messages['Public'][message_id]

                    date_int = this_massage['datetime']
                    data_datatime = datetime.datetime.fromtimestamp(date_int)

                    image_hash_name = this_massage.get('image_hash_name')
                    image_url = None
                    if image_hash_name:
                        image_url = image_api.get_original_image_url(image_hash_name)

                    all_public_messages.append({'id': message_id,
                                                'user': {'user': index, 'username': get_user_info_by_id(index).login},
                                                'datetime_format': data_datatime,
                                                'image_url': image_url,
                                                **this_massage})

        sorted_message = sorted(all_public_messages, key=lambda message: message['datetime'], reverse=True)

        return sorted_message[first_message:last_message]
