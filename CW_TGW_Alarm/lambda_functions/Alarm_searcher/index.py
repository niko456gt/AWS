import boto3
import json
import os

from datetime import datetime, timedelta

cloudwatch = boto3.client('cloudwatch')

def handler(event, context):

    # paremeters for namepsace and metric name
    namespace = "TAC_Monitoring Custom Metrics"
    dimension_name = "TransitGatewayID"
    #fetch the available metrics for the given namespace and dimension
    metrics = get_metrics(namespace, dimension_name)
    #fetch the metrics that do not have an alarm
    metrics_without_alarms = describe_alarms(metrics, namespace)
    for metric in metrics_without_alarms:
        metric_name = metric['MetricName']
        dimensions = metric['Dimensions']
        # get the value for the dimension we care about
        dimension_value = next((d['Value'] for d in dimensions if d['Name'] == dimension_name), None)
        if dimension_value:
            #create an alarm
            create_alarm(namespace, dimension_name, dimension_value,metric_name)
        else:
            print(f"Alarm already exists for metric: {metric_name}")

    #Same for VGW
    dimension_name = "VirtualGatewayID"
    #fetch the available metrics for the given namespace and dimension
    metrics = get_metrics(namespace, dimension_name)
    #fetch the metrics that do not have an alarm
    metrics_without_alarms = describe_alarms(metrics, namespace)
    for metric in metrics_without_alarms:
        metric_name = metric['MetricName']
        dimensions = metric['Dimensions']
        # get the value for the dimension we care about
        dimension_value = next((d['Value'] for d in dimensions if d['Name'] == dimension_name), None)
        if dimension_value:
            #create an alarm
            create_alarm(namespace, dimension_name, dimension_value,metric_name)
        else:
            print(f"Alarm already exists for metric: {metric_name}")
    #Same for TGW Attachment



  




  










    return {
        'statusCode': 200,
        'body': json.dumps('Alarm creation process completed.')
    }
def get_metrics(namespace, dimension_name):
    # Get the list of metrics for the given namespace and dimension name
    metrics = []
    paginator = cloudwatch.get_paginator('list_metrics')
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=10)  # Adjust the time range as needed

    #Step 1: List metrics for the specified namespace and dimension
    # Using a paginator to handle large sets of metrics

    for page in paginator.paginate(Namespace=namespace, Dimensions=[{'Name': dimension_name}]):
        for metric in page['Metrics']:
            # Step 2: we going to check it the metric has movement in the last 10 days
            try:
                response = cloudwatch.get_metric_statistics(
                    Namespace=namespace,
                    MetricName=metric['MetricName'], #Get_metric_statistics requires a metric name, quering the metric passed in the loop
                    Dimensions=metric['Dimensions'],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,  # 1 day in seconds, we are going to query any data at at all, so we just need 1 data point in the last 10 days
                    #This will reduce the execution time of the function.
                    Statistics=['SampleCount']
                )
                # Step 3: Check if there is any data point with a non-zero Sum value
                if response['Datapoints']:
                    metrics.append(metric)
            except Exception as e:
                print(f"Error processing metric {metric['MetricName']}: {e}")
    return metrics
""""
Looks at each metric in the specified namespace and dimension.

For each metric, checks if any datapoints exist in the past 10 days.

If there are datapoints → keeps it.

If not → skips it (stale/deleted resource).
"""


def describe_alarms(metrics,namespace):
    
    #Return list of metrics (name + dimensions) that do NOT have any associated alarms.
    metrics_without_alarms = []

    for metric in metrics:
        metric_name = metric['MetricName']
        dimensions = metric['Dimensions']

        response = cloudwatch.describe_alarms_for_metric(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=dimensions
        )

        if not response['MetricAlarms']:
            metrics_without_alarms.append({
                'MetricName': metric_name,
                'Dimensions': dimensions
            })

    return metrics_without_alarms
def create_alarm(namespace, dimension_name, dimension_value,metric_name):
    # Get the SNS topic ARN from the environment variable
    sns_topic_arn = os.environ['TOPIC_ARN']
    #create an alarm if it does not exist
    response = cloudwatch.put_metric_alarm(
        AlarmName=f'{dimension_value}_HEALTH_STATUS_CHECK',
        MetricName=metric_name,
        Namespace=namespace,
        Statistic='Average',
        Period=300,
        EvaluationPeriods=1,
        Threshold=1,
        TreatMissingData='breaching',
        AlarmActions=[sns_topic_arn],  # Replace with your SNS topic ARN
        ComparisonOperator='LessThanThreshold',
        Dimensions=[
            {
                'Name': dimension_name,
                'Value': dimension_value
            },
        ],
    )
    return response