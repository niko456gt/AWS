#!/usr/bin/env python3
import os

import aws_cdk as cdk



from cdk_fw.cdk_fw_stack import CdkFwStack


app = cdk.App()

env = cdk.Environment(account="288162407920", region="us-east-1")

CdkFwStack(app, "cdk-fw", env=env)


app.synth()
