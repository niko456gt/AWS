import requests
import json 
import boto3
from collections import defaultdict


ec2 = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')


def handler(event,context):
    PPSM_JSON = "https://raw.githubusercontent.com/niko456gt/AWS/refs/heads/main/cdk_PPSM/PPSM_Rules/rules.json"
    try:
        expected = fetch_expected_rules()
        actual = get_actual_sg_rules()

        compliant, non_compliant = compare_rules(expected, actual)

        publish_metrics_to_cloudwatch(len(compliant), len(non_compliant))

        return {
            "statusCode": 200,
            "body": json.dumps({
                "compliant": compliant,
                "non_compliant": non_compliant,
                "expected": expected,
                "actual": actual
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }



def normalize_description(desc):
    if not desc:
        return "Unknown"
    return desc.upper().strip()



def fetch_expected_rules():
    response = requests.get("https://raw.githubusercontent.com/niko456gt/AWS/refs/heads/main/cdk_PPSM/PPSM_Rules/rules.json")
    response.raise_for_status()
    rules = response.json()

    sg_data = defaultdict(lambda: [[], []])
    for rule in rules:
        low = rule.get('low port')
        high = rule.get('high port')
        protocol = rule.get('IP Protocol', 'Unknown')
        sg_name = rule.get('Security Group')

        if sg_name and low is not None and high is not None:
            sg_data[sg_name][0].append([low, high])
            sg_data[sg_name][1].append(normalize_description(protocol))

    return dict(sg_data)

def get_security_group_name(sg):
    tags = sg.get('Tags', [])
    for tag in tags:
        if tag.get('Key') == 'Name':
            return tag.get('Value')
    return sg.get('GroupName')

def get_actual_sg_rules():
    sg_data = defaultdict(lambda: [[], []])
    response = ec2.describe_security_groups()

    for sg in response['SecurityGroups']:
        name = get_security_group_name(sg)

        for rule in sg.get('IpPermissions', []):
            from_port = rule.get('FromPort')
            to_port = rule.get('ToPort')
            if from_port is None or to_port is None:
                continue

            protocol = rule.get('IpProtocol', 'Unknown')
            protocol = normalize_description(protocol)

            sg_data[name][0].append([from_port, to_port])
            sg_data[name][1].append(protocol)

    return dict(sg_data)


def compare_rules(expected, actual):
    compliant = []
    non_compliant = []

    for sg_name, expected_rules in expected.items():
        expected_ports, expected_protos = expected_rules
        actual_rules = actual.get(sg_name)

        if not actual_rules:
            non_compliant.append(sg_name)
            continue

        actual_ports, actual_protos = actual_rules

        if (
            sorted(expected_ports) == sorted(actual_ports) and
            sorted(p.upper() for p in expected_protos) == sorted(normalize_description(p) for p in actual_protos)
        ):
            compliant.append(sg_name)
        else:
            non_compliant.append(sg_name)

    return compliant, non_compliant


def publish_metrics_to_cloudwatch(compliant_count, non_compliant_count):
    cloudwatch.put_metric_data(
        Namespace='SecurityGroupCompliance',
        MetricData=[
            {
                'MetricName': 'ComplianceStatus',
                'Dimensions': [
                    {'Name': 'Status', 'Value': 'Compliant'}
                ],
                'Value': compliant_count,
                'Unit': 'Count'
            },
            {
                'MetricName': 'ComplianceStatus',
                'Dimensions': [
                    {'Name': 'Status', 'Value': 'NonCompliant'}
                ],
                'Value': non_compliant_count,
                'Unit': 'Count'
            }
        ]
    )