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

class LambdiniStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,topic, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        user_metric_namespace = "Custom/IAM"
        user_metric_name = "UserCount"


        #Lambda (As there is no resource type in cdk for this, we need to create a lambda function)
        metric_lambda = lambda_.Function(
            self, "TGW_Searcher",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=lambda_.Code.from_asset(str(Path(__file__).parent.parent / "lambda_functions/TGW_searcher")),
            timeout=Duration.seconds(30),
            initial_policy=[
                iam.PolicyStatement(
                    actions=["cloudwatch:PutMetricData",
                             "ec2:DescribeTransitGateways",
                             "elasticloadbalancing:DescribeLoadBalancers",
                             "ec2:DescribeTransitGatewayAttachments",
                             "directconnect:DescribeVirtualGateways"],
                    resources=["*"]
                )
            ]
        )
        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.rate(Duration.minutes(5))
        )
        rule.add_target(targets.LambdaFunction(metric_lambda))




        # lambda for alarm searcher
        alarm_lambda = lambda_.Function(
            self, "AlarmSearcher",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=lambda_.Code.from_asset(str(Path(__file__).parent.parent / "lambda_functions/Alarm_searcher")),
            timeout=Duration.seconds(30),
            environment={
                "TOPIC_ARN": topic.topic_arn
            },
            initial_policy=[
                iam.PolicyStatement(
                    actions=["cloudwatch:GetMetricData",
                             "cloudwatch:ListMetrics",
                             "cloudwatch:PutMetricAlarm",
                             "cloudwatch:DescribeAlarms",
                             "sns:Publish",],
                    resources=["*"]
                )
            ]
        )
        rule.add_target(targets.LambdaFunction(alarm_lambda))
        topic.grant_publish(alarm_lambda)