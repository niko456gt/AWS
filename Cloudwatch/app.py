#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cloudwatch.cloudwatch_stack import CloudwatchStack


app = cdk.App()
CloudwatchStack(app, "CloudwatchStack",
    env=cdk.Environment(
        account=os.getenv("replace_with_your_account_id"),
        region=os.getenv("replace_with_your_region"),
        )
    )

app.synth()
