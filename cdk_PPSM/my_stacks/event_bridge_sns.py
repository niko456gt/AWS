from aws_cdk import (
    Stack,
    aws_events as events,
    aws_events_targets as targets,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
)
from constructs import Construct


class SecurityGroupEventsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create SNS Topic
        sg_topic = sns.Topic(self, "SGEventNotifications", display_name="Security Group Ingress Events")

        # Optional: Email subscription
        sg_topic.add_subscription(
            subs.EmailSubscription("niko456gt@gmail.com") 
        )

        # Create EventBridge rule
        sg_event_rule = events.Rule(
            self, "SGIngressEventRule",
            description="Capture Authorize/RevokeSecurityGroupIngress API calls",
            event_pattern=events.EventPattern(
                source=["aws.ec2"],
                detail_type=["AWS API Call via CloudTrail"],
                detail={
                    "eventSource": ["ec2.amazonaws.com"],
                    "eventName": [
                        "AuthorizeSecurityGroupIngress",
                        "RevokeSecurityGroupIngress"
                    ]
                }
            )
        )

        # Add SNS as a target
        sg_event_rule.add_target(targets.SnsTopic(sg_topic))