# -*- coding: utf-8 -*-
import requests
import config

TRACK_URL_EVENT = "https://tracker.dashbot.io/track?platform=generic&v=10.1.1-rest&type=event&apiKey=" + config.dashbot_token


def track(message):

    data = {
        "name": message.text,  # event name
        "type": "customEvent",
        "userId": str(message.from_user.id),  # user id
        "extraInfo": {
            "firstname": message.from_user.first_name,
            "lastname": "" if message.from_user.last_name is None else message.from_user.last_name,
            "username": "" if message.from_user.username is None else "@" + message.from_user.username
        }

    }

    try:
        request_to_dashbot = requests.post(TRACK_URL_EVENT, json=data)
        print(request_to_dashbot.status_code, request_to_dashbot.reason)
    except Exception as e:
        print("Tracking was not successful:")
        print(e)
