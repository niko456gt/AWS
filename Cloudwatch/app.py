#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cloudwatch.cloudwatch_stack import CloudwatchStack


app = cdk.App()
CloudwatchStack(app, "CloudwatchStack",
    env=cdk.Environment(
        account=os.getenv("288162407920"),
        region=os.getenv("us-east-1"),
        )
    )

app.synth()
