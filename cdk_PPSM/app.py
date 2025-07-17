#!/usr/bin/env python3
import os
import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2

from my_stacks.lambda_stack import LambdaStack
from my_stacks.dashboard_stack import SgComplianceDashboardStack
from my_stacks.event_bridge_sns import SecurityGroupEventsStack 
from my_stacks.sec_group import AutoSgStack

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
SecurityGroupEventsStack(app, "SecurityGroupEventsStack")

vpc_id = "vpc-0123456789abcdef0"  # Replace with your actual VPC ID
vpc = ec2.Vpc.from_lookup(app, "ImportedVPC", vpc_id=vpc_id)
AutoSgStack(app, "AutoSgStack", vpc=vpc)

app.synth()
