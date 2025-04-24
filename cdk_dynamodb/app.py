#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_dynamodb.cdk_dynamodb_stack import CdkDynamodbStack


app = cdk.App()
CdkDynamodbStack(app, "CdkDynamodbStack",
    env=cdk.Environment(account="288162407920", region="us-east-1")

    )
app.synth()
