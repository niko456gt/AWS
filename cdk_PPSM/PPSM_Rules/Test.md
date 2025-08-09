# FRD Test Case -VDSS 2.1.2.5 :rocket:
## Overview :eyes:
This document outlines the proposal process for the log aquisition from the F5 and paloalto instances.
## 1. Prerequisites :pill:
    -AWS CDK and CLI Installed
    - AWS IAM Role configured for **IAM Roles Anywhere**
    - IAM Roles Anywhere Permissions:
        logs:CreateLogGroup
        logs:PutLogsEvents
        logs:CreateLogStream
        logs:DescribeLogStreams



---

flowchart TD
        A[EC2 Instance]


