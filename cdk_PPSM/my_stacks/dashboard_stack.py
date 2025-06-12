from aws_cdk import (
    Stack,
    Duration,
    aws_cloudwatch as cloudwatch,
)
from constructs import Construct

class SgComplianceDashboardStack(Stack):
      
      def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        
        dashboard = cloudwatch.Dashboard(
            self, "SgComplianceDashboard",
            dashboard_name="PPSM_SgComplianceDashboard"
        )

        # Metrics from Lambda
        compliant_metric = cloudwatch.Metric(
            namespace="SecurityGroupCompliance",
            metric_name="ComplianceStatus",
            dimensions_map={"Status": "Compliant"},
            label="Compliant",
            period=Duration.minutes(5),
            statistic="Sum"
        )

        noncompliant_metric = cloudwatch.Metric(
            namespace="SecurityGroupCompliance",
            metric_name="ComplianceStatus",
            dimensions_map={"Status": "NonCompliant"},
            label="NonCompliant",
            period=Duration.minutes(5),
            statistic="Sum"
        )
        # Pie widget
        pie_widget = cloudwatch.GraphWidget(
            title="Security Group Compliance",
            view=cloudwatch.GraphWidgetView.PIE,
            width=12,
            left=[compliant_metric, noncompliant_metric]
        )

        dashboard.add_widgets(pie_widget)