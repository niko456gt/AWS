import boto3
import json

def handler(event, context):
    # Create Boto3 clients for EC2, ELBV2 and CloudWatch
    ec2_client = boto3.client('ec2')
    cloudwatch_client = boto3.client('cloudwatch')
    elb_client = boto3.client('elbv2')
    vpg_client = boto3.client('directconnect')

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

    return (transitgateway_id,status_TGW,attachment_id,status_TGWA,load_balancer_name,load_balancer_state,virtualgateway_id,status_VPG)