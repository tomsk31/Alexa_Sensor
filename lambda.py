# -*- coding: utf-8 -*-

# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use this file except in
# compliance with the License. A copy of the License is located at
#
#    http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.

"""Alexa Smart Home Lambda Function Sample Code.
This file demonstrates some key concepts when migrating an existing Smart Home skill Lambda to
v3, including recommendations on how to transfer endpoint/appliance objects, how v2 and vNext
handlers can be used together, and how to validate your v3 responses using the new Validation
Schema.
Note that this example does not deal with user authentication, only uses virtual devices, omits
a lot of implementation and error handling to keep the code simple and focused.
"""

import logging
import time
import json
import uuid

# Imports for v3 validation
from validation import validate_message

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# To simplify this sample Lambda, we omit validation of access tokens and retrieval of a specific
# user's appliances. Instead, this array includes a variety of virtual appliances in v2 API syntax,
# and will be used to demonstrate transformation between v2 appliances and v3 endpoints.
SAMPLE_APPLIANCES = [
    {
        "applianceId": "endpoint-001",
        "manufacturerName": "TKT First",
        "modelName": "MOTION_SENSOR",
        "friendlyName": "Hall Switch",
        "friendlyDescription": "A switch that proactively reports",
    }
]

def lambda_handler(request, context):
    """Main Lambda handler.

    """

    try:
        logger.info("Directive:")
        logger.info(json.dumps(request, indent=4, sort_keys=True))

        if request["directive"]["header"]["name"] == "Discover":
            response = handle_discovery_v3(request)
        else:
            response = handle_non_discovery_v3(request)

        logger.info("Response:")
        logger.info(json.dumps(response, indent=4, sort_keys=True))

        return response

    except ValueError as error:
        logger.error(error)
        raise


# handlers
def handle_discovery_v3(request):
    endpoints = []
    for appliance in SAMPLE_APPLIANCES:
        endpoints.append(get_endpoint_from_appliance(appliance))

    response = {
        "event": {
            "header": {
                "namespace": "Alexa.Discovery",
                "name": "Discover.Response",
                "payloadVersion": "3",
                "messageId": get_uuid()
            },
            "payload": {
                "endpoints": endpoints
            }
        }
    }
    return response

def handle_non_discovery_v3(request):
    request_namespace = request["directive"]["header"]["namespace"]
    request_name = request["directive"]["header"]["name"]

    if request_namespace == "Alexa.ReportState":
        response = reportState(request)

    elif request_namespace == "Alexa.Authorization":
        if request_name == "AcceptGrant":
            response = {
                "event": {
                    "header": {
                        "namespace": "Alexa.Authorization",
                        "name": "AcceptGrant.Response",
                        "payloadVersion": "3",
                        "messageId": "5f8a426e-01e4-4cc9-8b79-65f8bd0fd8a4"
                    },
                    "payload": {}
                }
            }
            return response
    else:


# utility functions
def reportState(request)
{
           state = {
           		"event": {
                	"header": {
                    	"namespace": "Alexa",
                    	"name": "StateReport",
                    	"payloadVersion": "3",
                    	"messageId": get_uuid(),
                    	"correlationToken": request["directive"]["header"]["correlationToken"]
                		},
                	"endpoint": {
                    	"scope": {
                        	"type": "BearerToken",
                        	"token": token
                    		},
                    	"endpointId":
                		},
                	"context": {
		                "properties": [
        		            {
                	        "namespace": "Alexa.MotionSensor",
                	        "name": "detectionState",
                	        "value": "NOT_CONNECTED",
                    	    "timeOfSample": get_utc_timestamp(),
                        	"uncertaintyInMilliseconds": 500
                    		},
                    		{
        					"namespace": "Alexa.EndpointHealth",
        					"name": "connectivity",
        					"value": {
          						"value": "OK"
        						},
        					"timeOfSample": "2017-02-03T16:20:50.52Z",
        					"uncertaintyInMilliseconds": 0
      						}
                		]
		            },
        	        "payload": {}
            	}
        	}
        return state

def get_endpoint_from_appliance(appliance):
    endpoint = {
        "endpointId": appliance["applianceId"],
        "manufacturerName": appliance["manufacturerName"],
        "friendlyName": appliance["friendlyName"],
        "description": appliance["friendlyDescription"],
        "displayCategories": appliance["modelName"],
        "capabilities": []
    }
    endpoint["capabilities"] = get_capabilities(appliance)
    return endpoint

def get_capabilities(appliance):
    model_name = appliance["modelName"]
    if model_name == 'MOTION_SENSOR':
        capabilities = [
            {
                "type": "AlexaInterface",
                "interface": "Alexa.MotionSensor",
                "version": "3",
                "properties": {
                    "supported": [
                        { "name": "detectionState" }
                    ],
                    "proactivelyReported": True,
                    "retrievable": True
                }
            }
        ]
    # additional capabilities that are required for each endpoint
    endpoint_health_capability = {
        "type": "AlexaInterface",
        "interface": "Alexa.EndpointHealth",
        "version": "3",
        "properties": {
            "supported":[
                { "name":"connectivity" }
            ],
            "proactivelyReported": True,
            "retrievable": True
        }
    }
    alexa_interface_capability = {
        "type": "AlexaInterface",
        "interface": "Alexa",
        "version": "3"
    }
    capabilities.append(endpoint_health_capability)
    capabilities.append(alexa_interface_capability)
    return capabilities