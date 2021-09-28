
# Cisco DNA Center Compliance APIs Use Cases


This repo is for an application that will verify the Cisco DNA Center managed devices compliance state.

When events are received, the webhook receiver will execute this workflow :
- identify if the issue is "active" or "resolved", ignore if issue is "resolved"
- parse the event notification and identify:
    - the Cisco DNA Center IP address reporting the issue
    - reporting device details - management IP address, serial number, device type, location, software version
    - provide links to Cisco DNA Center Issue Details, Device 360 View, Device Compliance Status
- sync the network device
- trigger and verify compliance status for the device
- use the Command Runner APIs to collect the running and startup configuration
- identify if there are differences and create an Ansible playbook to remediate the config change
- continuously post messages to Webex room to update the network team of all the completed steps
- upload the Ansible playbook to the Webex room and provide the command to execute the playbook

This app is to be used only in demo or lab environments, it is not written for production networks.


**Cisco Products & Services:**

- Cisco DNA Center, Webex Teams

**Tools & Frameworks:**

- Python environment to run the application, Webex Teams Bot to send notifications
- Cisco DNA Center Python SDK, Cisco DNA Center Ansible Collection

**Usage**

Sample Output:

-------

Webhook Received
Payload:
{'version': '1.0.0', 'instanceId': '9916e734-c7b6-4203-a6ce-4ea9e9f6001a', 'eventId': 'NETWORK-NON-FABRIC_WIRED-1-251', 'namespace': 'ASSURANCE', 'name': None, 'description': None, 'type': 'NETWORK', 'category': 'ALERT', 'domain': 'Connectivity', 'subDomain': 'Non-Fabric Wired', 'severity': 1, 'source': 'ndp', 'timestamp': 1632779770234, 'details': {'Type': 'Network Device', 'Assurance Issue Details': 'Interface GigabitEthernet2 (Interface description: TO_CSR2_GI2) connecting the following two network devices is down: Local Node: PDX-RO, Peer Node: PDX-RO', 'Assurance Issue Priority': 'P1', 'Device': '10.93.141.23', 'Assurance Issue Name': 'Interface GigabitEthernet2 (Interface description: TO_CSR2_GI2) is Down on Network Device 10.93.141.23', 'Assurance Issue Category': 'Connectivity', 'Assurance Issue Status': 'active'}, 'ciscoDnaEventLink': 'https://10.93.141.45/dna/assurance/issueDetails?issueId=9916e734-c7b6-4203-a6ce-4ea9e9f6001a', 'note': 'To programmatically get more info see here - https://<ip-address>/dna/platform/app/consumer-portal/developer-toolkit/apis?apiId=8684-39bb-4e89-a6e4', 'context': None, 'userId': None, 'i18n': None, 'eventHierarchy': None, 'message': None, 'messageParams': None, 'parentInstanceId': None, 'network': None, 'dnacIP': '10.93.141.45'}


Event Id: NETWORK-NON-FABRIC_WIRED-1-251
Event Details: Interface GigabitEthernet2 (Interface description: TO_CSR2_GI2) connecting the following two network devices is down: Local Node: PDX-RO, Peer Node: PDX-RO
Cisco DNA Center Reporting the issue: 10.93.141.45
Device Management IP Address: 10.93.141.23
Device Hostname: PDX-RO
Device Id: 01f7cdf2-2298-42c7-bb74-dc68e3c3a051

Cisco DNA Center notification message posted

Device Family: CSR1000V
Device OS Version: 17.3.2
Device Serial Number: 92ML86IWCBN
Device Location: Global/OR/PDX-1/Floor 2

Device Details message posted
Wait for Config Compliance timer

Wait for 180 seconds
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Device re-sync started, wait for re-sync to complete

Wait for 180 seconds
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Compliance Task Id: 0dcb12f3-a7dd-4dbf-9d27-c18877d30e54

Wait for 30 seconds
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Compliance check status: Compliance report has been generated successfully
Compliance Type: PSIRT , Status: COMPLIANT
Compliance Type: IMAGE , Status: COMPLIANT
Compliance Type: APPLICATION_VISIBILITY , Status: COMPLIANT
Compliance Type: RUNNING_CONFIG , Status: NON_COMPLIANT

Compliance Status message posted

Wait for Command Runner APIs tasks to complete

Wait for 30 seconds
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

The show running file id: e713bde0-5974-412c-840f-f46c770a34aa
The show startup-config file id: 9b7998cb-3a9f-4a75-b377-c296b8a53b69
The running config and startup config have been collected and saved to files


The Config Diff:
 
 interface GigabitEthernet2
  description TO_CSR2_GI2
  ip address 10.93.140.25 255.255.255.252
  ip nbar protocol-discovery
+ shutdown
  negotiation auto
  cdp enable
  arp timeout 300
 
-router bgp 65002
- no bgp log-neighbor-changes
- timers bgp 15 45 30
- neighbor 10.93.140.26 remote-as 65004
- neighbor 10.93.140.26 ebgp-multihop 5
- neighbor 10.93.141.17 remote-as 65003
- neighbor 10.93.141.17 ebgp-multihop 5
- neighbor 10.93.141.42 remote-as 65001
- neighbor 10.93.141.42 ebgp-multihop 5
-
- address-family ipv4
-  network 10.93.141.23 mask 255.255.255.255
-  neighbor 10.93.140.26 activate
-  neighbor 10.93.141.17 activate
-  neighbor 10.93.141.42 activate
- exit-address-family


Config Diff Webex message posted

Remediation CLI Template:
 
 interface GigabitEthernet2
  description TO_CSR2_GI2
  ip address 10.93.140.25 255.255.255.252
  ip nbar protocol-discovery
no shutdown
  negotiation auto
  cdp enable
  arp timeout 300
 
router bgp 65002
 no bgp log-neighbor-changes
 timers bgp 15 45 30
 neighbor 10.93.140.26 remote-as 65004
 neighbor 10.93.140.26 ebgp-multihop 5
 neighbor 10.93.141.17 remote-as 65003
 neighbor 10.93.141.17 ebgp-multihop 5
 neighbor 10.93.141.42 remote-as 65001
 neighbor 10.93.141.42 ebgp-multihop 5
 
 address-family ipv4
  network 10.93.141.23 mask 255.255.255.255
  neighbor 10.93.140.26 activate
  neighbor 10.93.141.17 activate
  neighbor 10.93.141.42 activate
 exit-address-family


Ansible Playbook uploaded to Webex
10.93.141.45 - - [27/Sep/2021 15:03:42] "POST /compliance_check HTTP/1.1" 202 –

Webhook Received
Payload:
{'version': '1.0.0', 'instanceId': '9916e734-c7b6-4203-a6ce-4ea9e9f6001a', 'eventId': 'NETWORK-NON-FABRIC_WIRED-1-251', 'namespace': None, 'name': None, 'description': None, 'type': 'NETWORK', 'category': 'ALERT', 'domain': 'Connectivity', 'subDomain': 'Non-Fabric Wired', 'severity': 1, 'source': 'Cisco DNA Assurance', 'timestamp': 1632780360300, 'details': {'Type': 'Network Device', 'Assurance Issue Details': 'Interface GigabitEthernet2 (Interface description: TO_CSR2_GI2) connecting the following two network devices is down: Local Node: PDX-RO, Peer Node: PDX-RO', 'Assurance Issue Priority': 'P1', 'Device': '10.93.141.23', 'Assurance Issue Name': 'Interface GigabitEthernet2 (Interface description: TO_CSR2_GI2) is Down on Network Device 10.93.141.23', 'Assurance Issue Category': 'Connectivity', 'Assurance Issue Status': 'resolved'}, 'ciscoDnaEventLink': 'https://10.93.141.45/dna/assurance/issueDetails?issueId=9916e734-c7b6-4203-a6ce-4ea9e9f6001a', 'note': 'To programmatically get more info see here - https://<ip-address>/dna/platform/app/consumer-portal/developer-toolkit/apis?apiId=8684-39bb-4e89-a6e4', 'context': None, 'userId': None, 'i18n': None, 'eventHierarchy': None, 'message': None, 'messageParams': None, 'parentInstanceId': None, 'network': None, 'dnacIP': '10.93.141.45'}

10.93.141.45 - - [27/Sep/2021 15:06:10] "POST /compliance_check HTTP/1.1" 202 -


-------

 Thank you @jbogarin for contributions to this use case

**License**

This project is licensed to you under the terms of the [Cisco Sample Code License](./LICENSE).


