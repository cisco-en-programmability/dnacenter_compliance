#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2021 Cisco and/or its affiliates.
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


import os
import time
import requests
import urllib3
import json

from flask import Flask, request
from flask_basicauth import BasicAuth
from requests.auth import HTTPBasicAuth  # for Basic Auth
from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
from dotenv import load_dotenv
from dnacentersdk import DNACenterAPI

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

load_dotenv('environment.env')

WEBHOOK_USERNAME = os.getenv('WEBHOOK_USERNAME')
WEBHOOK_PASSWORD = os.getenv('WEBHOOK_PASSWORD')

DNAC_URL = os.getenv('DNAC_URL')
DNAC_USER = os.getenv('DNAC_USER')
DNAC_PASS = os.getenv('DNAC_PASS')

os.environ['TZ'] = 'America/Los_Angeles'  # define the timezone for PST
time.tzset()  # adjust the timezone, more info https://help.pythonanywhere.com/pages/SettingTheTimezone/

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = WEBHOOK_USERNAME
app.config['BASIC_AUTH_PASSWORD'] = WEBHOOK_PASSWORD
# app.config['BASIC_AUTH_FORCE'] = True  # enable if all API endpoints support HTTP basic auth

basic_auth = BasicAuth(app)

DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)


def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data: data to pretty print
    :return None
    """
    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


def time_sleep(time_sec):
    """
    This function will wait for the specified time_sec, while printing a progress bar, one '!' / second
    Sample Output :
    Wait for 10 seconds
    !!!!!!!!!!
    :param time_sec: time, in seconds
    :return: none
    """
    print('\nWait for ' + str(time_sec) + ' seconds')
    for i in range(time_sec):
        print('!', end='')
        time.sleep(1)
    return



@app.route('/')  # create a decorator for testing the Flask framework
@basic_auth.required
def index():
    return '<h1>Flask Receiver App is Up!</h1>', 200


@app.route('/compliance_check', methods=['POST'])  # API endpoint to receive the client detail report
@basic_auth.required
def client_report():
    if request.method == 'POST':
        print('Webhook Received')
        webhook_json = request.json

        # print the received notification
        print('Payload: ')
        print(webhook_json, '\n')

        # create a DNACenterAPI "Connection Object"
        dnac_api = DNACenterAPI(username=DNAC_USER, password=DNAC_PASS, base_url=DNAC_URL, version='2.2.2.3', verify=False)

        # identify what type of event notification was received
        event_id = webhook_json['eventId']
        print('\nEvent Id:', event_id)

        # parse the payload for the event, and select device info
        device_management_ip = webhook_json['details']['Device']
        print('Device Management IP Address:', device_management_ip)
        device_info = dnac_api.devices.get_network_device_by_ip(ip_address=device_management_ip)
        device_hostname = device_info['response']['hostname']
        print('Device Hostname:', device_hostname)
        device_id = device_info['response']['id']
        print('Device Id:', device_id)

        # check compliance
        run_compliance = dnac_api.compliance.run_compliance(deviceUuids=[device_id])
        compliance_task_id = run_compliance['response']['taskId']
        print('Compliance Task Id:', compliance_task_id)

        # wait for 15 seconds for compliance checks to complete
        time_sleep(15)

        # check task by id
        task_info = dnac_api.task.get_task_by_id(task_id=compliance_task_id)
        task_result = task_info['response']['progress']
        print('\nCompliance check status:', task_result)

        # retrieve the compliance status
        compliance_info = dnac_api.compliance.compliance_details_of_device(device_uuid=device_id)
        print(compliance_info)

        return 'Notification Received', 202
    else:
        return 'Method not supported', 405


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, ssl_context='adhoc')
