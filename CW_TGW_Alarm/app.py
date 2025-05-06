#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cw_tgw_alarm.cw_tgw_alarm_stack import CwTgwAlarmStack
from lambdini_stack.lambdini_stack import LambdiniStack


app = cdk.App()

cw_stack =CwTgwAlarmStack(app, "CwTgwAlarmStack",
        env=cdk.Environment(
            account=os.getenv("needupdate"),
            region=os.getenv("us-east-1"),
            )      
        )
LambdiniStack(app, "LambdiniStack",
    topic=cw_stack.topic,
    env=cdk.Environment(
        account=os.getenv("needupdate"),
        region=os.getenv("us-east-1"),
        )
              )

app.synth()
