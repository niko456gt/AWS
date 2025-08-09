import boto3
import json
 
cloudwatch = boto3.client('cloudwatch')
 
def lambda_handler(event, context):
 
    namespace = "TAC_Monitoring Custom Metrics"
    dimension_names = ["TransitGatewayID","AttachmentId","LoadBalancerName","VirtualGatewayID","TransitGatewayConnectPeerID"]
    # Create Boto3 clients for EC2, ELBV2 and CloudWatch
    ec2_client = boto3.client('ec2')
    cloudwatch_client = boto3.client('cloudwatch')
    elb_client = boto3.client('elbv2')
    vpg_client = boto3.client('directconnect')
 
    #Collect active resource IDs
    active_resources = {
    "TransitGatewayID": set(),
    "AttachmentId": set(),
    "LoadBalancerName": set(),
    "VirtualGatewayID": set(),
    "TransitGatewayConnectPeerID": set()
     }
 
 
    # Call describe_transit_gateways to get a list of transit gateways
    response_TGW = ec2_client.describe_transit_gateways()  
    TGWs = response_TGW['TransitGateways']  
    print(TGWs) #Displays in CloudWatch Logs
 
    #Iterate through the TGWs to determine status
    for gateway in TGWs:
        transitgateway_id = gateway['TransitGatewayId']
        status_TGW = gateway['State']
        print(transitgateway_id,status_TGW) #Displays in CloudWatch Logs
 
    #Determine the Cloudwatch Metric Value based on the status
        if status_TGW == 'available':
            metric_value_TGW = 1 #status is Active
            active_resources["TransitGatewayID"].add(transitgateway_id) #Populates 'active_resources'
        else:
            metric_value_TGW = 0 # status is anything else
 
    # Send the status' as  metrics to CloudWatch
        cloudwatch_client.put_metric_data(
            Namespace='TAC_Monitoring Custom Metrics',  # Custom namespace for your metrics
            MetricData = [
                {
                    "MetricName" : f'TGWStatus_{transitgateway_id}',  # Metric name
                    "Dimensions" : [
                    {
                    'Name': 'TransitGatewayID',
                    'Value': transitgateway_id  # Use the transit gateway name as a dimension
                    },
                ],
                "Value" : metric_value_TGW,  # 1 for available, 0 for other statuses
                "Unit" : "Count"
                }
            ]
            )
 
    # Describe the transit gateway attachments
    response_TGWA = ec2_client.describe_transit_gateway_attachments()
    attachments = response_TGWA['TransitGatewayAttachments']
    print(attachments)    
    # Iterate through the attachments to determine status
    for attachment in attachments:
        attachment_id = attachment['TransitGatewayAttachmentId']
        status_TGWA = attachment['State']
        print(attachment_id,status_TGWA)    
    # Determine the CloudWatch metric value based on the status
        if status_TGWA == 'available':
           metric_value_TGWA = 1  # Status is 'available'
           active_resources["AttachmentId"].add(attachment_id) #Populates 'active_resources'
        else:
            metric_value_TGWA = 0  # Status is anything else
           
    # Send the status' as  metrics to CloudWatch
        cloudwatch_client.put_metric_data(
            Namespace='TAC_Monitoring Custom Metrics',  # Custom namespace for your metrics
            MetricData = [
                {
                    "MetricName" : f'TGWAttachmentStatus_{attachment_id}',  # Metric name
                    "Dimensions" : [
                    {
                    'Name': 'AttachmentId',
                    'Value': attachment_id  # Use the attachment ID as a dimension
                    },
                ],
                "Value" : metric_value_TGWA,  # 1 for available, 0 for other statuses
                "Unit" : "Count"
                }
            ]
            )
       
    # Call describe_load_balancers to get a list of load balancers
    response_ELB = elb_client.describe_load_balancers()  
    ELBs = response_ELB['LoadBalancers']  
    print(ELBs)
 
    #Iterate through the ELBs to determine status
    for lb in ELBs:
        load_balancer_name = lb['LoadBalancerName']
        load_balancer_arn = lb['LoadBalancerArn']
        load_balancer_state = lb['State']['Code']
        print(load_balancer_name,load_balancer_state)
 
    #Determine the CLoudwatch Metric Value based on the state
        if load_balancer_state == 'active':
            metric_value_ELB = 1 #status is Active
            active_resources["LoadBalancerName"].add(load_balancer_name) #Populates 'active_resources'
        else:
            metric_value_ELB = 0 # status is anything else
    # Send the status' as  metrics to CloudWatch
        cloudwatch_client.put_metric_data(
            Namespace='TAC_Monitoring Custom Metrics',  # Custom namespace for your metrics
            MetricData = [
                {
                    "MetricName" : f'LoadBalancerStatus_{load_balancer_name}',  # Metric name
                    "Dimensions" : [
                    {
                    'Name': 'LoadBalancerName',
                    'Value': load_balancer_name  # Use the load balancer name as a dimension
                    },
                ],
                "Value" : metric_value_ELB,  # 1 for available, 0 for other statuses
                "Unit" : "Count"
                }
            ]
            )
 
    # Call describe_transit_gateways to get a list of transit gateways
    response_VPG = vpg_client.describe_virtual_gateways()  
    VPGs = response_VPG['virtualGateways']  
    print(VPGs)
 
    #Iterate through the TGWs to determine status
    for gateway in VPGs:
        virtualgateway_id = gateway['virtualGatewayId']
        status_VPG = gateway['virtualGatewayState']
        print(virtualgateway_id,status_VPG)
 
    #Determine the Cloudwatch Metric Value based on the status
        if status_VPG == 'available':
            metric_value_VPG = 1 #status is Active
            active_resources["VirtualGatewayID"].add(virtualgateway_id) #Populates 'active_resources'
        else:
            metric_value_VPG = 0 # status is anything else
 
    # Send the status' as  metrics to CloudWatch
        cloudwatch_client.put_metric_data(
            Namespace='TAC_Monitoring Custom Metrics',  # Custom namespace for your metrics
            MetricData = [
                {
                    "MetricName" : f'VPGStatus_{virtualgateway_id}',  # Metric name
                    "Dimensions" : [
                    {
                    'Name': 'VirtualGatewayID',
                    'Value': virtualgateway_id  # Use the transit gateway name as a dimension
                    },
                ],
                "Value" : metric_value_VPG,  # 1 for available, 0 for other statuses
                "Unit" : "Count"
                }
            ]
            )  
 
    # Call describe_transit_gateway_connect_peers to get a list of BGP connect peers
    response_TGWCP = ec2_client.describe_transit_gateway_connect_peers()  
    TGWCPs = response_TGWCP['TransitGatewayConnectPeers']  
    print(TGWCPs) #Displays in CloudWatch Logs
 
    #Iterate through the TGWCPs to determine BGPstatus
    for peers in TGWCPs:
        transitgatewayconnectpeer_id = peers['TransitGatewayConnectPeerId']
        status_BGP = peers['ConnectPeerConfiguration']['BgpConfigurations'][0]['BgpStatus']
        print(transitgatewa yconnectpeer_id,status_BGP) #Displays in CloudWatch Logs
 
    #Determine the Cloudwatch Metric Value based on the status
        if status_BGP == 'up':
            metric_value_BGP = 1 #status is Active
            active_resources["TransitGatewayConnectPeerID"].add(transitgatewayconnectpeer_id) #Populates 'active_resources'
        else:
            metric_value_BGP = 0 # status is anything else
 
    # Send the status' as  metrics to CloudWatch
        cloudwatch_client.put_metric_data(
            Namespace='TAC_Monitoring Custom Metrics',  # Custom namespace for your metrics
            MetricData = [
                {
                    "MetricName" : f'BGPStatus_{transitgatewayconnectpeer_id}',  # Metric name
                    "Dimensions" : [
                    {
                    'Name': 'TransitGatewayConnectPeerID',
                    'Value': transitgatewayconnectpeer_id  # Use the BGP Peer Connection name as a dimension
                    },
                ],
                "Value" : metric_value_BGP,  # 1 for available, 0 for other statuses
                "Unit" : "Count"
                }
            ]
            )    
    for dimension_name in dimension_names:
        create_alarm_for_metrics(namespace,dimension_name,active_resources[dimension_name])  
        print(f'⚠️ Created alarms for {dimension_name} with active resources: {active_resources[dimension_name]}')
    #return (transitgateway_id,status_TGW,attachment_id,status_TGWA,load_balancer_name,load_balancer_state,virtualgateway_id,status_VPG,transitgatewayconnectpeer_id,status_BGP)
 
 
 
 
 
def create_alarm_for_metrics(namespace, dimension_name,active_resource_ids):
    #Fetching the available metrics based on args
    metrics = get_metrics(namespace,dimension_name)
    #Fetch metrics without alarm
    metrics_without_alarm = describe_alarms(metrics,namespace)
 
    for metric in metrics_without_alarm:
        metric_name = metric['MetricName']
        dimensions = metric['Dimensions']
 
        # get the value for the dimension needed for the alarm
        dimension_value = next((d['Value'] for d in dimensions if d['Name']== dimension_name), None)
        if dimension_value not in active_resource_ids:
            continue
           
        if dimension_value:
            create_alarm(namespace,dimension_name,dimension_value,metric_name)
        else:
            pass
def describe_alarms(metrics,namespace):
    cloudwatch = boto3.client('cloudwatch')
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
        AlarmActions=["arn:aws-us-gov:sns:us-gov-west-1:076531663898:AWS_TAC_DASHBOARD_ALARM_NOTIFICATION"],  # Replace with your SNS topic ARN
        ComparisonOperator='LessThanThreshold',
        Dimensions=[
            {
                'Name': dimension_name,
                'Value': dimension_value
            },
        ],
    )
    return response
def get_metrics(namespace, dimension_name):
    # Get the list of metrics for the given namespace and dimension name
    metrics = []
    paginator = cloudwatch.get_paginator('list_metrics')
 
    for page in paginator.paginate(Namespace=namespace, Dimensions=[{'Name': dimension_name}]):
        metrics.extend(page['Metrics'])
 
    return metrics
 