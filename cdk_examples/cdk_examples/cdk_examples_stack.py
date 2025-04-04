from aws_cdk import core as cdk
from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    ws_iam as iam,

    # aws_sqs as sqs,
)
from constructs import Construct

class CdkExamplesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "CdkExamplesQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
