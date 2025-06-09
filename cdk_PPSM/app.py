#!/usr/bin/env python3
import os
import aws_cdk as cdk

from my_stacks.lambda_stack import lambda_stack


app = cdk.App()
PPSM_Stack = lambda_stack(app, "CdkPpsmStack",
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    )
)

app.synth()
