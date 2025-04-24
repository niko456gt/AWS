
from aws_cdk import (
    # Duration,
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    # aws_sqs as sqs,
)
from constructs import Construct

class CdkDynamodbStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        #create a dynamodb table
        table = dynamodb.Table(self,
        "NWFW-Table",
        partition_key=dynamodb.Attribute(
            name="sid",
            type=dynamodb.AttributeType.STRING
        ),
        billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        encryption=dynamodb.TableEncryption.DEFAULT,
        removal_policy=RemovalPolicy.DESTROY

    )
