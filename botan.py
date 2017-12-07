# -*- coding: utf-8 -*-
import requests
import json

TRACK_URL = 'https://api.botan.io/track'

def make_json(message):
    data = {}
    data['message_id'] = message.message_id
    data['from'] = {}
    data['from']['id'] = message.from_user.id
    data['from']['name'] = message.from_user.first_name + ("" if message.from_user.last_name is None else " " + message.from_user.last_name) + ("" if message.from_user.username is None else " @" + message.from_user.username)
    data['chat'] = {}
    data['chat']['id'] = message.chat.id
    return data


def track(token, uid, message, name='Message'):
    try:
        r = requests.post(
            TRACK_URL,
            params={"token": token, "uid": uid, "name": name},
            data=make_json(message),
            headers={'Content-type': 'application/json'},
        )
        return r.json()
    except requests.exceptions.Timeout:
        # set up for a retry, or continue in a retry loop
        print('ERROR IN requests.exceptions.Timeout :')
        return False
    except requests.exceptions.RequestException as e:
        print('ERROR IN requests.exceptions.RequestException :')
        print(e)
        return False
    except ValueError as e:
        print('ERROE IN ValueError :')
        print(e)
        print(message)
        print(make_json(message))
        print(type(make_json(message)))
        return False
