import datetime
from typing import OrderedDict

from firebase_db.image_api import ImageAPI
from users_db.user_api import get_user_info_by_id


image_api = ImageAPI()


def messages_organization(messages: OrderedDict, user_id: int = None) -> list[dict]:
    messages = ordereddict_to_list_dict(messages)
    messages = make_image_url(messages)
    messages = make_datetime_format(messages)

    if user_id:
        messages = input_user_info(messages, user_id)

    return messages


def ordereddict_to_list_dict(messages: OrderedDict) -> list[dict]:
    list_dict = []

    for message_id in messages:
        list_dict.append({
            'id': message_id,
            **messages[message_id]
        })

    return list_dict


def make_image_url(messages: list[dict]) -> list[dict]:
    for message in messages:
        image_hash_name = message.get('image_hash_name')
        if image_hash_name:
            message['image_url'] = image_api.get_original_image_url(image_hash_name)

    return messages


def make_datetime_format(messages: list[dict]) -> list[dict]:
    for message in messages:
        date_int = message['datetime']
        data_datatime = datetime.datetime.fromtimestamp(date_int)

        message['datetime_format'] = data_datatime

    return messages


def input_user_info(messages: list[dict], user_id: int) -> list[dict]:
    for message in messages:
        message['user'] = {'user': user_id, 'username': get_user_info_by_id(user_id).login}

    return messages


def sort_message(messages: list[dict]) -> list[dict]:
    return sorted(messages, key=lambda message: message['datetime'], reverse=True)
