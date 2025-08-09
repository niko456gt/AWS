# FRD Test Case -VDSS 2.1.2.11 :rocket:
## Overview :eyes:
This document outlines the process of manual, standard, and automated processes when testing the VDSS features 2.1.2.11.
## 1. Prerequisites :pill:
    -AWS CDK and CLI Installed
    - AWS IAM Role configured for **IAM Roles Anywhere**
    - IAM Roles Anywhere Permissions:
        cloudwatch:ListMetrics
        logs:CreateLogGroup
        logs:PutLogsEvents
        lambda:InvokeFunction

---
## Variables
    There are no visible variables for this testing requirement
## Monitoring :eyes:
    -Cloudwatch alarms:
        -name of alarm:
        -functionality of alarm
    -Cloudwatch metrics 
        -name of metric:
        -values needed for testing:
    -sqs Queue:
        -name of Queue:

## Execution / Testing Process
    -Manual:
        Invoke the Lammbda function:
            This sends a log to the S3 bucket, Which is then proccessed by the SQS queue.
        Check the SQS Queue for message movement.
        check Cloudwatch metrics for:
            NumberOfMEssagesDeleted
            NumberOfMessagesReceived
        Both metrics should show a value greater than 0 for message movements.
        Confirm that the Message succesfully leaves the queue, deleted by the Sentinel agent.
    -Standard 
        All logs are tracked, encrypted, and monitored by Cloudtrail into s3()
        All logs in S3 ingress the SQS Queue()
        All logs must egress from the SQS queue by the Centinel agent calling the SQS API.
        If an error occurs and the message does not leave the queue, The EHM Monitoring team and dashboard are notified by a cloudWatch alarm()
    -Automation (Proposal)
        update the SQS Queue to implement Dead-letter queue for message retry and notification of unproccessed messages.

## Common Issues and fixes
| Issue | Fix | 
|:-------|:-----|
|Egress logs costs|Implement in-house processing|
|Unable to track SQS Queue calls | Use AWS Cloudwatch metrics instead|
|Alarms being created(False negative) | Arbitrary number for the Cloudwatch alarm|
# Notes :pencil2:
+ Keep track of Egress Log costs.
+ Use version control (git) to manage infrastructe code.
+ Bootstraping increases readiness for deployment.
+ SQS Queue limitations and speed.
+ Consider a internal Processing message system.

# Lessons learned
 - Verify SQS Limitations on retention periods for cost management
 - Verify SQS API Calls are being triggered by Role, not by SQS
# Sample Code Snippet 
```

import json
import logging
import time
import boto3
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Optional: Push logs to CloudWatch Logs explicitly (if needed)
log_group_name = '/vdss/test/logs'
log_stream_name = 'vdss-log-stream'

logs_client = boto3.client('logs')

def ensure_log_stream_exists():
    try:
        logs_client.create_log_group(logGroupName=log_group_name)
    except logs_client.exceptions.ResourceAlreadyExistsException:
        pass

    try:
        logs_client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
    except logs_client.exceptions.ResourceAlreadyExistsException:
        pass

def put_log_event(message):
    timestamp = int(time.time() * 1000)
    sequence_token = None
    try:
        response = logs_client.describe_log_streams(logGroupName=log_group_name, logStreamNamePrefix=log_stream_name)
        sequence_token = response['logStreams'][0].get('uploadSequenceToken')
    except Exception as e:
        logger.error(f"Error describing log streams: {str(e)}")

    kwargs = {
        'logGroupName': log_group_name,
        'logStreamName': log_stream_name,
        'logEvents': [{
            'timestamp': timestamp,
            'message': message
        }]
    }

    if sequence_token:
        kwargs['sequenceToken'] = sequence_token

    logs_client.put_log_events(**kwargs)

def lambda_handler(event, context):
    ensure_log_stream_exists()
    
    test_log_event = {
        "timestamp": str(datetime.utcnow()),
        "event": "TestEvent",
        "source": "LambdaFunctionTest",
        "message": "This is a simulated log event for VDSS 2.1.2.11 testing."
    }

    log_message = json.dumps(test_log_event)
    logger.info(log_message)
    put_log_event(log_message)

    return {
        'statusCode': 200,
        'body': json.dumps('Log event successfully generated for VDSS compliance test.')
    }
```