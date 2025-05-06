from aws_cdk import (
    aws_sns as sns,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct

class CwTgwAlarmStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.topic = sns.Topic(self, "AWS_TAC_DASHBOARD",
            display_name="AWS TAC Dashboard",
            topic_name="AWS_TAC_DASHBOARD",
        )