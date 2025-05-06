import boto3
import json

cloudwatch = boto3.client('cloudwatch')

def handler(event, context):
    # paremeters for namepsace and metric name
    namespace = "TAC_Monitoring Custom Metrics"
    dimmension_name = "TransitGatewayID"
    #fetch the available metrics for the given namespace and dimension
    metrics = get_metrics(namespace, dimmension_name)
    for metric in metrics:
        metric_name = metric['MetricName']
        dimension_value = metric['Dimensions'][0]['Value']
        #check if an alarm exists for the metric
        existing_alarms = describe_alarms(metric_name)
        if not existing_alarms:
            #create an alarm if it does not exist
            create_alarm(namespace, dimmension_name, dimension_value,metric_name)
        else:
            print(f"Alarm already exists for metric: {metric_name}")
    #Same for TGW Attachment



    dimmension_name = "AttachmentId"
    metrics = get_metrics(namespace, dimmension_name)
    for metric in metrics:
        metric_name = metric['MetricName']
        dimension_value = metric['Dimensions'][0]['Value']
        #check if an alarm exists for the metric
        existing_alarms = describe_alarms(metric_name)
        if not existing_alarms:
            #create an alarm if it does not exist
            create_alarm(namespace, dimmension_name, dimension_value,metric_name)
        else:
            print(f"Alarm already exists for metric: {metric_name}")


    dimmension_name = "LoadBalancerName"
    metrics = get_metrics(namespace, dimmension_name)
    for metric in metrics:
        metric_name = metric['MetricName']
        dimension_value = metric['Dimensions'][0]['Value']
        #check if an alarm exists for the metric
        existing_alarms = describe_alarms(metric_name)
        if not existing_alarms:
            #create an alarm if it does not exist
            create_alarm(namespace, dimmension_name, dimension_value,metric_name)
        else:
            print(f"Alarm already exists for metric: {metric_name}")


        








    return {
        'statusCode': 200,
        'body': json.dumps('Alarm creation process completed.')
    }
def get_metrics(namespace, dimmension_name):
    #fetch the available metrics for the given namespace and dimension
    response = cloudwatch.list_metrics(
        Namespace=namespace,
        Dimensions=[
            {
                'Name': dimmension_name,
            },
        ]
    )
    return response['Metrics']
def describe_alarms(metric_name):
    #check if an alarm exists for the metric
    response = cloudwatch.describe_alarms(
        AlarmNamePrefix=metric_name,
    )
    return response['MetricAlarms']
def create_alarm(namespace, dimmension_name, dimension_value,metric_name):
    #create an alarm if it does not exist
    response = cloudwatch.put_metric_alarm(
        AlarmName=f'{metric_name}_Alarm',
        MetricName=metric_name,
        Namespace=namespace,
        Statistic='Average',
        Period=300,
        EvaluationPeriods=1,
        Threshold=1,
        ComparisonOperator='LessThanThreshold',
        Dimensions=[
            {
                'Name': dimmension_name,
                'Value': dimension_value
            },
        ],
    )
    return response