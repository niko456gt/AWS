import boto3
import json
                                    
def handler(event, context):
    ec2_client = boto3.client('ec2')
    cloudwatch = boto3.client('cloudwatch')
    #Call describe_transit_gateway_attachments to get the list of TGW
    response_TGW = ec2_client.describe_transit_gateways()
    TGWs = response_TGW['TransitGateways']
    print("TGWs: ", TGWs)
    #Iterate through the TGW to determine status
    for gateway in TGWs:
        transitgateway_id = gateway['TransitGatewayId']
        status_TGW = gateway['State']
        print(transitgateway_id, status_TGW) #Display in Cloudwatch logs
    #Determine the cloudwatch metric value based on the status
        if status_TGW == 'available':
            metric_value = 1 #Active
        else:
            metric_value = 0 #verify if the status is not available
        
                                    
        cloudwatch.put_metric_data(
            Namespace='TAC_Monitoring Custom Metrics',
            MetricData = [
                {
                    "MetricName" : f'TGWStatus_{transitgateway_id}',
                    "Dimensions" : [
                    {
                    'Name': 'TransitGateway_ID',
                    'Value': transitgateway_id
                                    },],
                "Value" : metric_value,
                "Unit" : "Count"
                                    }
                                    ]
                                    )
    return(transitgateway_id)