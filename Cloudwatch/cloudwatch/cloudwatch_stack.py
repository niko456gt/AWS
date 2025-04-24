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
from constructs import Construct

class CloudwatchStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        user_metric_namespace = "Custom/IAM"
        user_metric_name = "UserCount"


        #Lambda (As there is no resource type in cdk for this, we need to create a lambda function)
        metric_lambda = lambda_.Function(
            self, "IAMUserCounter",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=lambda_.InlineCode("""
import boto3
                                    
def handler(event, context):
    iam = boto3.client('iam')
    cloudwatch = boto3.client('cloudwatch')
    # variable to get list of users
    users = iam.list_users()['Users']
    # variable to get the count of users
    user_count = len(users)
    # put metric data
    cloudwatch.put_metric_data(
        Namespace='Custom/IAM',
        MetricData=[
            {
                'MetricName': 'UserCount',
                'Value': user_count,
                'Unit': 'Count'
            },
        ]
    )
    return {
        'statusCode': 200,
        'body': 'User count: ' + str(user_count)
    }
        
                                    
    })
            """),
            timeout=Duration.seconds(30),
            initial_policy=[
                iam.PolicyStatement(
                    actions=["iam:ListUsers","cloudwatch:PutMetricData"],
                    resources=["*"]
                )
            ]
        )


        #cloudwatch alarm
        cw.Alarm(
            self, "IAMUserCountAlarm",
            metric=cw.Metric(
                metric_name=user_metric_name,
                namespace=user_metric_namespace,
                statistic="Average",
                period=Duration.minutes(5),
            ),
            comparison_operator=cw.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            threshold=3,
            evaluation_periods=1,
            period=Duration.minutes(5),
            alarm_description="Alarm when user count is greater than 3",
        )
# the only thing is mandatory is the MFA.
# policy Force_MFA.
        