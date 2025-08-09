# FRD Test Case -VDSS 2.1.2.5 :rocket:
## Overview :eyes:
This document outlines the proposal process for the log aquisition from the F5 and Palo Alto instances.
## 1. Prerequisites :pill:
    -AWS CDK and CLI Installed
    - AWS IAM Role configured for **IAM Roles Anywhere**
    - IAM Roles Anywhere Permissions:
        logs:CreateLogGroup
        logs:PutLogsEvents
        logs:CreateLogStream
        logs:DescribeLogStreams



---
```mermaid
flowchart TD
    A[EC2 Instance] -->B[Cloudwatch Agent]
    B --> C[CloudWatch Logs/CloudWatch Metrics]
    C --> D[CloudWatch Log Group]
    D --> E[CloudWatch Subscription Filter / Export Task]
    E --> F[Amazon S3 Bucket]
    F --> G[Data Available for Later Analysis]

    B -.-> H(Collects system metrics and application logs / Define what are we logging )
    D -.-> HD(Organizes logs into named groups for retention)
    E -.-> HE(Filters or transforms logs before delivery to S3)
    F -.-> HF(Stores encrypted data for later querying or processing)