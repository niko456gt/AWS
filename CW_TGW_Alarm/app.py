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
        account=os.getenv("replace_with_your_account_id"),
        region=os.getenv("replace_with_your_region"),
        )       
              )

app.synth()
