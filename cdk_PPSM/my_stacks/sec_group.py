from aws_cdk import (
    Stack,
    aws_ec2 as ec2
)
from constructs import Construct

class AutoSgStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the Security Group
        auto_sg = ec2.SecurityGroup(
            self, "AutoSecurityGroup",
            vpc=vpc,
            security_group_name="auto_sg",
            description="Security group for automated ppsm rules testing",
            allow_all_outbound=False
        )