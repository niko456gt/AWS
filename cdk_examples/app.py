#!/usr/bin/env python3
import os

import aws_cdk as cdk

from lib.stacks.ec2.webapp import WebAppStack


app = cdk.App()


WebAppStack(
    app,
    "WebAppStack",
    env=cdk.Environment(
            account="your_account_id",  # Replace with your AWS account ID
            region="us-east-1",
        ),
    vpc_id="YOUR_VPC_ID",  # Replace with your VPC ID
    subnet_ids="you subnet_ids",  # Replace with your subnet IDs
)
app.synth()
