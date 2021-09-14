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
import difflib
import webex_apis
import yaml
import logging

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

WEBEX_BOT_AUTH = os.getenv('WEBHOOKD_BOT_AUTH')
WEBEX_URL = os.getenv('WEBEX_URL')
WEBEX_ROOM = os.getenv('WEBHOOKD_ROOM')

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


def compare_configs(cfg1, cfg2):
    """
    This function, using the unified diff function, will compare two config files and identify the changes.
    '+' or '-' will be prepended in front of the lines with changes
    :param cfg1: old configuration file path and filename
    :param cfg2: new configuration file path and filename
    :return: text with the configuration lines that changed. The return will include the configuration for the sections
    that include the changes
    """

    # open the old and new configuration files
    f1 = open(cfg1, 'r')
    old_cfg = f1.readlines()
    f1.close()

    f2 = open(cfg2, 'r')
    new_cfg = f2.readlines()
    f2.close()

    # compare the two specified config files {cfg1} and {cfg2}
    d = difflib.unified_diff(old_cfg, new_cfg, n=9)

    # create a diff_list that will include all the lines that changed
    # create a diff_output string that will collect the generator output from the unified_diff function
    diff_list = []
    diff_output = ''

    for line in d:
        diff_output += line
        if line.find('xxxx') == -1:
            if line.find('quit') == -1:
                if (line.find('+++') == -1) and (line.find('---') == -1):
                    if (line.find('-!') == -1) and (line.find('+!') == -1):
                        if line.startswith('+'):
                            diff_list.append('\n' + line)
                        elif line.startswith('-'):
                            diff_list.append('\n' + line)

    # process the diff_output to select only the sections between '!' characters for the sections that changed,
    # replace the empty '+' or '-' lines with space
    diff_output = diff_output.replace('+!', '!')
    diff_output = diff_output.replace('-!', '!')
    diff_output_list = diff_output.split('!')

    all_changes = []

    for changes in diff_list:
        for config_changes in diff_output_list:
            if changes in config_changes:
                if config_changes not in all_changes:
                    all_changes.append(config_changes)

    # create a config_text string with all the sections that include changes
    config_text = ''
    for items in all_changes:
        config_text += items

    return config_text


@app.route('/')  # create a decorator for testing the Flask framework
@basic_auth.required
def index():
    return '<h1>Flask Receiver App is Up!</h1>', 200


@app.route('/compliance_check', methods=['POST'])  # API endpoint to receive the client detail report
@basic_auth.required
def compliance_check():

    # logging, debug level, to file {application_run.log}
    logging.basicConfig(
        filename='application_run.log',
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    if request.method == 'POST':
        print('Webhook Received')
        webhook_json = request.json

        # print the received notification
        print('Payload: ')
        print(webhook_json, '\n')

        # check if a new open issue, ignore if an resolved issue notification
        issue_status = webhook_json['details']['Assurance Issue Status']
        if issue_status == 'resolved':
            return 'Notification Received', 202

        # identify the Cisco DNA Center reporting the issue
        dnac_ip = webhook_json['dnacIP']
        dnac_url = 'https://' + dnac_ip

        # create a DNACenterAPI "Connection Object"
        dnac_api = DNACenterAPI(username=DNAC_USER, password=DNAC_PASS, base_url=dnac_url, version='2.2.2.3', verify=False)

        # identify what type of event notification was received
        event_id = webhook_json['eventId']
        print('\nEvent Id:', event_id)

        # identify the event details
        event_details = webhook_json['details']['Assurance Issue Details']
        print('Event Details:', event_details)
        print('Cisco DNA Center Reporting the issue:', dnac_ip)
        event_link = webhook_json['ciscoDnaEventLink']

        # parse the payload for the event, and select device info
        device_management_ip = webhook_json['details']['Device']
        print('Device Management IP Address:', device_management_ip)
        device_info = dnac_api.devices.get_network_device_by_ip(ip_address=device_management_ip)
        device_hostname = device_info['response']['hostname']
        print('Device Hostname:', device_hostname)
        device_id = device_info['response']['id']
        print('Device Id:', device_id)

        # post message to Webex Room
        room_id = webex_apis.get_room_id(WEBEX_ROOM)

        card_message = {
            "roomId": room_id,
            "parentId": None,
            "markdown": "Cisco DNA Center Notification",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.0",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "Cisco DNA Center Notification",
                                "weight": "bolder",
                                "size": "large"
                            },
                            {
                                "type": "FactSet",
                                "facts": [
                                    {
                                        "title": "Assurance Issue Details:",
                                        "value": event_details
                                    },
                                    {
                                        "title": "Device Hostname:",
                                        "value": device_hostname
                                    },
                                    {
                                        "title": "Device Management IP:",
                                        "value":device_management_ip
                                    },
                                    {
                                        "title": "Cisco DNA Center IP",
                                        "value": dnac_ip
                                    }
                                ]
                            }
                        ],
                        "actions": [
                            {
                                "type": "Action.openURL",
                                "title": "Cisco DNA Center Issue Details",
                                "url": event_link
                            }
                        ]
                    }
                }
            ]
        }

        response = webex_apis.post_room_card_message(WEBEX_ROOM, card_message)
        response_json = response.json()
        message_id = response_json['id']

        print('\nCisco DNA Center notification message posted')

        # collect device detail info
        device_detail_response = dnac_api.devices.get_device_detail(identifier='uuid',search_by=device_id)
        device_detail_json = device_detail_response['response']
        device_sn = device_detail_json['serialNumber']
        device_os_version = device_detail_json['softwareVersion']
        device_family = device_detail_json['platformId']
        device_location = device_detail_json['location']

        print('\nDevice Family:', device_family)
        print('Device OS Version:', device_os_version)
        print('Device Serial Number:', device_sn)
        print('Device Location:', device_location)

        time.sleep(1)
        card_message = {
            "roomId": room_id,
            "parentId": message_id,
            "markdown": "Device Details",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.0",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "Cisco DNA Center Device Details",
                                "weight": "bolder"
                            },
                            {
                                "type": "FactSet",
                                "facts": [
                                    {
                                        "title": "Family:",
                                        "value": device_family
                                    },
                                    {
                                        "title": "Serial Number:",
                                        "value": device_sn
                                    },
                                    {
                                        "title": "OS Version:",
                                        "value": device_os_version
                                    },
                                    {
                                        "title": "Location",
                                        "value": device_location
                                    }
                                ]
                            },
                            {
                                "type": "TextBlock",
                                "wrap": True,
                                "text": "Collecting Compliance information, this will take few minutes"
                            }
                        ],
                        "actions": [
                            {
                                "type": "Action.openURL",
                                "title": "Device 360 View",
                                "url": 'https://10.93.141.45/dna/assurance/device/details?id=' + device_id
                            }
                        ]
                    }
                }
            ]
        }

        response = webex_apis.post_room_card_message(WEBEX_ROOM, card_message)

        print('\nDevice Details message posted\nWait for Config Compliance timer')
        time_sleep(180)

        # re-sync device
        resync = dnac_api.devices.sync_devices_using_forcesync(force_sync=True, payload=[device_id])
        print('\n\nDevice re-sync started, wait for re-sync to complete')
        time_sleep(120)

        # check compliance
        run_compliance = dnac_api.compliance.run_compliance(deviceUuids=[device_id])
        compliance_task_id = run_compliance['response']['taskId']
        print('\n\nCompliance Task Id:', compliance_task_id)

        # wait for 30 seconds for compliance checks to complete
        time_sleep(60)

        # check task by id
        task_info = dnac_api.task.get_task_by_id(task_id=compliance_task_id)
        task_result = task_info['response']['progress']
        print('\n\nCompliance check status:', task_result)

        # retrieve the compliance status
        compliance_info = dnac_api.compliance.compliance_details_of_device(device_uuid=device_id)
        compliance_info_json = compliance_info['response']
        compliance_status = {}
        facts = []  # to be used for the adaptive cards message
        for check in compliance_info_json:
            print('Compliance Type:', check['complianceType'], ', Status:', check['status'])
            compliance_status.update({check['complianceType']: check['status']})
            facts.append({'title': check['complianceType'], 'value': check['status']})

        # update Webex room with compliance result
        card_message = {
            "roomId": room_id,
            "parentId": message_id,
            "markdown": "Device Compliance",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.0",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "Device Compliance",
                                "weight": "bolder"
                            },
                            {
                                "type": "FactSet",
                                "facts": facts
                            }
                        ],
                        "actions": [
                            {
                                "type": "Action.openURL",
                                "title": "Device Compliance",
                                "url": 'https://10.93.141.45/dna/provision/devices/inventory/device-details?deviceId=' + device_id + '&defaultTab=Summary'
                            }
                        ]
                    }
                }
            ]
        }
        response = webex_apis.post_room_card_message(WEBEX_ROOM, card_message)

        print('\nCompliance Status message posted')

        # check config compliance state
        if compliance_status['RUNNING_CONFIG'] == 'NON_COMPLIANT':
            # trigger workflow to identify what has changed

            # send command runner API for "show run" and "show start"
            show_run_result = dnac_api.command_runner.run_read_only_commands_on_devices(deviceUuids=[device_id], commands=['show running-config'])
            show_run_task_id = show_run_result['response']['taskId']
            time.sleep(5)  # for pacing the API calls
            show_start_result = dnac_api.command_runner.run_read_only_commands_on_devices(deviceUuids=[device_id], commands=['show startup-config'])
            show_start_task_id = show_start_result['response']['taskId']

            # wait for Command Runner APIs to execute
            print('\nWait for Command Runner APIs tasks to complete')
            time_sleep(30)

            # collect the show running output file
            show_run_task_result = dnac_api.task.get_task_by_id(task_id=show_run_task_id)
            show_run_file_info = show_run_task_result['response']['progress']
            show_run_file_id = json.loads(show_run_file_info)['fileId']
            print('\n\nThe show running file id:', show_run_file_id)

            show_run_file_result = dnac_api.file.download_a_file_by_fileid(file_id=show_run_file_id, save_file=False)
            # the function will return data encoded using
            # <https://urllib3.readthedocs.io/en/latest/reference/urllib3.response.html>

            # retrieve the running config
            show_run_file_json = json.loads(show_run_file_result.data.decode('utf-8'))
            show_run_file_content = show_run_file_json[0]['commandResponses']['SUCCESS']['show running-config'].replace('show running-config','')

            # remove all the config lines before version
            show_run_file_updated = show_run_file_content.split('version')[1]

            # save the running config to file
            run_file = device_hostname + '_run.txt'
            f_temp = open(run_file, 'w')
            f_temp.write(show_run_file_updated)
            f_temp.seek(0)  # reset the file pointer to 0
            f_temp.close()

            # collect the show startup-config output file
            show_start_task_result = dnac_api.task.get_task_by_id(task_id=show_start_task_id)
            show_start_file_info = show_start_task_result['response']['progress']
            show_start_file_id = json.loads(show_start_file_info)['fileId']
            print('The show startup-config file id:', show_start_file_id)

            show_start_file_result = dnac_api.file.download_a_file_by_fileid(file_id=show_start_file_id, save_file=False)
            # the function will return data encoded using
            # <https://urllib3.readthedocs.io/en/latest/reference/urllib3.response.html>

            # retrieve the startup config
            show_start_file_json = json.loads(show_start_file_result.data.decode('utf-8'))
            show_start_file_content = show_start_file_json[0]['commandResponses']['SUCCESS']['show startup-config'].replace(
                'show startup-config', '')

            # remove all the config lines before version
            show_start_file_updated = show_start_file_content.split('version')[1]

            # save the startup config to file
            start_file = device_hostname + '_start.txt'
            f_temp = open(start_file, 'w')
            f_temp.write(show_start_file_updated)
            f_temp.seek(0)  # reset the file pointer to 0
            f_temp.close()

            print('The running config and startup config have been collected and saved to files')

            # check for the config diff
            diff_result = compare_configs(start_file, run_file)
            print('\n\nThe Config Diff:\n', diff_result)

            # save the diff to file
            diff_file = device_hostname + '_diff.txt'
            f_temp = open(diff_file, 'w')
            f_temp.write(diff_result)
            f_temp.seek(0)  # reset the file pointer to 0
            f_temp.close()

            body = [
                {
                    "type": "TextBlock",
                    "text": "Device Configuration Changes",
                    "weight": "bolder"
                },
                {
                    "type": "TextBlock",
                    "wrap": True,
                    "text": "There are differences between the \nRunning Configuration and Start Configuration."
                },
                {
                    "type": "TextBlock",
                    "wrap": True,
                    "text": "Lines marked wth '+' have been added to the Running Configuration, \nLines marked with '-' have been removed from the Running Configuration"
                }
            ]

            with open(diff_file) as file:
                line = file.readline()
                count = 1
                while line:
                    line_update = line.replace('\n', '')
                    first_character = line_update[0]
                    if first_character == '-':
                        line_final = "'-'     " + line_update[1:]
                    else:
                        if first_character == '+':
                            line_final = "'+'     " + line_update[1:]
                        else:
                            line_final = line
                    body.append({'type': 'TextBlock', 'text': line_final, "wrap": True, "color": "attention"})
                    line = file.readline()
                    count += 1

            card_message = {
                "roomId": room_id,
                "parentId": message_id,
                "markdown": "Device Configuration Changes",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": {
                            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                            "type": "AdaptiveCard",
                            "version": "1.0",
                            "body": body
                        }
                    }
                ]
            }

            response = webex_apis.post_room_card_message(WEBEX_ROOM, card_message)

            print('\nConfig Diff Webex message posted')

            # prepare CLI templates
            diff_result_update = diff_result.replace('\n+', '\nno')
            diff_result_final = diff_result_update.replace('\n-', '\n')

            print('\nRemediation CLI Template:\n', diff_result_final)

            # create Ansible Playbook
            source_file = "project.yml"
            ansible_file = device_hostname + '.yml'

            with open(source_file) as file:
                data_list = yaml.load(file, Loader=yaml.SafeLoader)

            data_dict = data_list[0]
            data_dict['vars']['cli_template'] = diff_result_final

            final_data = [data_dict]

            with open(ansible_file, 'w') as file:
                yaml.dump(final_data, file, default_flow_style=False)

            # upload the file to Webex
            card_message = {
                "roomId": room_id,
                "parentId": message_id,
                "markdown": "Ansible Playbook",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": {
                            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                            "type": "AdaptiveCard",
                            "version": "1.0",
                            "body": [
                                {
                                    "type": "TextBlock",
                                    "text": "Ansible Playbook",
                                    "weight": "bolder"
                                },
                                {
                                    "type": "TextBlock",
                                    "wrap": True,
                                    "text": "Here is attached the Ansible Playbook to remediate the configuration drift"
                                },
                                {
                                    "type": "TextBlock",
                                    "wrap": True,
                                    "text": "Execute the attached file by using the command:\n"
                                },
                                {
                                    "type": "TextBlock",
                                    "wrap": True,
                                    "text": 'ansible-playbook -e "device_name=' + device_hostname + ' dnac_host=' + dnac_ip + '" ' + ansible_file
                                }
                            ]
                        }
                    }
                ]
            }

            response = webex_apis.post_room_card_message(WEBEX_ROOM, card_message)
            time.sleep(2)
            response = webex_apis.post_room_file(WEBEX_ROOM, ansible_file, 'text/plain', message_id)

            print('\nAnsible Playbook uploaded to Webex')

        return 'Notification Received', 202
    else:
        return 'Method not supported', 405


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, ssl_context='adhoc')
