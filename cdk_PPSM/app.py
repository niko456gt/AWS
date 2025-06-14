#!/usr/bin/env python3
import os
import aws_cdk as cdk

from my_stacks.lambda_stack import LambdaStack
from my_stacks.dashboard_stack import SgComplianceDashboardStack


app = cdk.App()
PPSM_Stack = LambdaStack(app, "CdkPpsmStack",
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    )
)
PPSM_Dashboard = SgComplianceDashboardStack(app, "SgComplianceDashboardStack",
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    )
)

app.synth()
