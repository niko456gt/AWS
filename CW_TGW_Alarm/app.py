#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cw_tgw_alarm.cw_tgw_alarm_stack import CwTgwAlarmStack
from lambdini_stack.lambdini_stack import LambdiniStack


app = cdk.App()
CwTgwAlarmStack(app, "CwTgwAlarmStack",
    
    )
LambdiniStack(app, "LambdiniStack",
    env=cdk.Environment(
        account=os.getenv("288162407920"),
        region=os.getenv("us-east-1"),
        )       
              )

app.synth()
