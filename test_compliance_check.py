#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Copyright (c) 2022 Cisco and/or its affiliates.

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
import json
import urllib3
import time
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth  # for Basic Auth
from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

load_dotenv('environment.env')

WEBHOOK_USERNAME = os.getenv('WEBHOOK_USERNAME')
WEBHOOK_PASSWORD = os.getenv('WEBHOOK_PASSWORD')

DNAC_URL = os.getenv('DNAC_URL')
DNAC_USER = os.getenv('DNAC_USER')
DNAC_PASS = os.getenv('DNAC_PASS')

os.environ['TZ'] = 'America/Los_Angeles'  # define the timezone for PST
time.tzset()  # adjust the timezone, more info https://help.pythonanywhere.com/pages/SettingTheTimezone/

basic_auth = HTTPBasicAuth(WEBHOOK_USERNAME, WEBHOOK_PASSWORD)

dnac_param = {
    "version": "1.0.0",
    "instanceId": "96cd9e29-9f81-49fa-8fb7-ef77a40b9ee7",
    "eventId": "NETWORK-NETWORKS-2-303",
    "namespace": "ASSURANCE",
    "name": "",
    "description": "",
    "type": "NETWORK",
    "category": "ERROR",
    "domain": "Know Your Network",
    "subDomain": "Networks",
    "severity": 2,
    "source": "ndp",
    "timestamp": 1631223562928,
    "details": {
        "Type": "Network Device",
        "Assurance Issue Priority": "P2",
        "Assurance Issue Details": "Device name: PDX-RO - BGP peering with neighbor 10.93.141.42 failed due to Autonomous System (AS) Number mismatch. The configured AS number does not match with peer",
        "Device": "10.93.141.23",
        "Assurance Issue Name": "Device PDX-ACCESS Received Error Message From Neighbor 10.93.141.42 (Peer in Wrong AS)",
        "Assurance Issue Category": "connectivity",
        "Assurance Issue Status": "active"
    },
    "ciscoDnaEventLink": "https://10.93.141.45/dna/assurance/issueDetails?issueId=96cd9e29-9f81-49fa-8fb7-ef77a40b9ee7",
    "note": "To programmatically get more info see here - https://<ip-address>/dna/platform/app/consumer-portal/developer-toolkit/apis?apiId=8684-39bb-4e89-a6e4",
    "context": "",
    "userId": "",
    "i18n": "",
    "eventHierarchy": "",
    "message": "",
    "messageParams": "",
    "parentInstanceId": "",
    "network": "",
    "dnacIP": "10.93.141.45"
}

dnac_param_resolved = {
    "version": "1.0.0",
    "instanceId": "96cd9e29-9f81-49fa-8fb7-ef77a40b9ee7",
    "eventId": "NETWORK-NETWORKS-2-303",
    "namespace": "ASSURANCE",
    "name": "",
    "description": "",
    "type": "NETWORK",
    "category": "ERROR",
    "domain": "Know Your Network",
    "subDomain": "Networks",
    "severity": 2,
    "source": "ndp",
    "timestamp": 1631223562928,
    "details": {
        "Type": "Network Device",
        "Assurance Issue Priority": "P2",
        "Assurance Issue Details": "Device name: PDX-RO - BGP peering with neighbor 10.93.141.42 failed due to Autonomous System (AS) Number mismatch. The configured AS number does not match with peer",
        "Device": "10.93.141.23",
        "Assurance Issue Name": "Device PDX-RO Received Error Message From Neighbor 10.93.141.42 (Peer in Wrong AS)",
        "Assurance Issue Category": "connectivity",
        "Assurance Issue Status": "resolved"
    },
    "ciscoDnaEventLink": "https://10.93.141.35/dna/assurance/issueDetails?issueId=96cd9e29-9f81-49fa-8fb7-ef77a40b9ee7",
    "note": "To programmatically get more info see here - https://<ip-address>/dna/platform/app/consumer-portal/developer-toolkit/apis?apiId=8684-39bb-4e89-a6e4",
    "context": "",
    "userId": "",
    "i18n": "",
    "eventHierarchy": "",
    "message": "",
    "messageParams": "",
    "parentInstanceId": "",
    "network": "",
    "dnacIP": "10.93.141.35"
}


# test the Webhook with a Cisco DNA Center notification

url = 'Add_Your_Webhook_Destination'
header = {'content-type': 'application/json'}
response = requests.post(url, auth=basic_auth, data=json.dumps(dnac_param), headers=header, verify=False)
print('\n', response.status_code, response.text)
