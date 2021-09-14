#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Copyright (c) 2019 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

__author__ = "Gabriel Zapodeanu TME, ENB"
__email__ = "gzapodea@cisco.com"
__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2021 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import requests
import urllib3
import json
import os

from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
from dotenv import load_dotenv
from requests_toolbelt.multipart.encoder import MultipartEncoder

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

load_dotenv('environment.env')

WEBEX_BOT_AUTH = os.getenv('WEBHOOKD_BOT_AUTH')
WEBEX_URL = os.getenv('WEBEX_URL')
WEBEX_ROOM = os.getenv('WEBHOOKD_ROOM')
WEBEX_BOT_ID = os.getenv('WEBHOOKD_BOT_ID')


def get_room_id(room_name):
    """
    This function will find the Webex Teams room id based on the {room_name}
    Call to Webex - /rooms
    :param room_name: The Webex Teams room name
    :return: the Webex Teams room Id
    """
    room_id = None
    url = WEBEX_URL + '/rooms' + '?max=1000'
    header = {'content-type': 'application/json', 'authorization': WEBEX_BOT_AUTH}
    room_response = requests.get(url, headers=header, verify=False)
    room_list_json = room_response.json()
    room_list = room_list_json['items']
    for rooms in room_list:
        if rooms['title'] == room_name:
            room_id = rooms['id']
    return room_id


def post_room_message(room_name, message):
    """
    This function will post the {message} to the Webex Teams room with the {room_name}
    Call to function get_room_id(room_name) to find the room_id
    Followed by API call /messages
    :param room_name: the Webex Teams room name
    :param message: the text of the message to be posted in the room
    :return: none
    """
    room_id = get_room_id(room_name)
    payload = {'roomId': room_id, 'text': message}
    url = WEBEX_URL + '/messages'
    header = {'content-type': 'application/json', 'authorization': WEBEX_BOT_AUTH}
    requests.post(url, data=json.dumps(payload), headers=header, verify=False)


def post_room_markdown_message(room_name, message):
    """
    This function will post a markdown {message} to the Webex Teams room with the {room_name}
    Call to function get_room_id(room_name) to find the room_id
    Followed by API call /messages
    :param room_name: the Webex Teams room name
    :param message: the text of the markdown message to be posted in the room
    :return: none
    """
    room_id = get_room_id(room_name)
    payload = {'roomId': room_id, 'markdown': message}
    url = WEBEX_URL + '/messages'
    header = {'content-type': 'application/json', 'authorization': WEBEX_BOT_AUTH}
    requests.post(url, data=json.dumps(payload), headers=header, verify=False)


def post_room_url_message(room_name, message, url):
    """
    This function will post an URL to the Webex Teams room with the {room_name}
    Call to function get_room_id(room_name) to find the room_id
    Followed by API call /messages
    :param room_name: the Webex Teams room name
    :param message: the text of the markdown message to be posted in the room
    :param url: URL for the text message
    :return: none
    """
    room_id = get_room_id(room_name)
    payload = {'roomId': room_id, 'markdown': ('[' + message + '](' + url + ')')}
    url = WEBEX_URL + '/messages'
    header = {'content-type': 'application/json', 'authorization': WEBEX_BOT_AUTH}
    requests.post(url, data=json.dumps(payload), headers=header, verify=False)


def get_bot_message_by_id(message_id, bot_id):
    """
    This function will get the message content using the {message_id}
    :param message_id: Webex Teams message_id
    :param bot_id: the Bot id to validate message
    :return: message content
    """
    url = WEBEX_URL + '/messages/' + message_id
    header = {'content-type': 'application/json', 'authorization': WEBEX_BOT_AUTH}
    response = requests.get(url, headers=header, verify=False)
    response_json = response.json()
    all_people = response_json['mentionedPeople']
    for people in all_people:
        if people == bot_id:
            return response_json['text']
    return None


def post_room_card_message(room_name, card_message):
    """
    This function will post a adaptive card message {card_message} to the Webex Teams room with the {room_name}
    :param room_name: Webex Teams message
    :param card_message: card message
    :return: none
    """
    room_id = get_room_id(room_name)
    url = WEBEX_URL + '/messages'
    header = {'content-type': 'application/json', 'authorization': WEBEX_BOT_AUTH}
    response = requests.post(url, data=json.dumps(card_message), headers=header, verify=False)
    return response


def upload_file_message(room_name, file_name):
    """
    This function will upload a the file with the name {file_name} to the room with the name {room_name}
    :param room_name: Webex room name
    :param file_name: file name
    :return: response
    """
    room_id = get_room_id(room_name)
    url = WEBEX_URL + '/messages'
    m = MultipartEncoder({'roomId': room_id, 'text': 'Ansible Playbook', 'files': (file_name, open(file_name, 'rb'))})
    header = {'content-type': 'application/json', 'authorization': WEBEX_BOT_AUTH}
    response = requests.post(url, data=m, headers=header, verify=False)
    print(response.status_code, response.text)
    return response


def post_room_file(room_name, file_name, file_type, parent_id):
    """
    This function will post the file with the name {file_name}, type of file {file_type},
    from the local folder with the path {file_path}, to the Spark room with the name {room_name}
    Call to function get_room_id(room_name) to find the room_id
    Followed by API call /messages
    :param room_name: Spark room name
    :param file_name: File name to be uploaded
    :param file_type: File type
    :param parent_id: the message parent id to reply to, if available
    :return: response
    """

    room_id = get_room_id(room_name)
    m = MultipartEncoder({'roomId': room_id, 'parentId': parent_id, 'text': 'Ansible Playbook',
                          'files': (file_name, open(file_name, 'rb'), file_type)})
    url = WEBEX_URL + '/messages'
    header = {'Authorization': WEBEX_BOT_AUTH, 'Content-Type': m.content_type}
    response = requests.post(url, data=m, headers=header)


