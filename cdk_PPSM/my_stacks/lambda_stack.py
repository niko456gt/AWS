from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda as lambda_,
    aws_cloudwatch as cw
    # aws_sqs as sqs,
)
from pathlib import Path
from constructs import Construct

class LambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)



        #Lambda (As there is no resource type in cdk for this, we need to create a lambda function)
        PPSM_lambda = lambda_.Function(
            self, "PPSM_Monitoring",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=lambda_.Code.from_asset(str(Path(__file__).parent.parent / "lambda_functions/PPSM_monitoring")),
            timeout=Duration.seconds(30),
            description="Monitoring of PPSM rules",
            initial_policy=[
                iam.PolicyStatement(
                    actions=["ec2:DescribeSecurityGroups",
                             "cloudwatch:PutMetricData",
                             "cloudwatch:describeLogStreams",],
                    resources=["*"]
                )
            ]
        )

""""
        rule = events.Rule(
            self, "Rule",
            rule_name="PPSM_Monitoring_Rule",
            description="Cron Job to monitor PPSM rules",
            schedule=events.Schedule.rate(Duration.minutes(5))
        )
        rule.add_target(targets.LambdaFunction(PPSM_lambda))
"""



