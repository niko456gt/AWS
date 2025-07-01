import requests
import json 
import boto3
from collections import defaultdict
import re


ec2 = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')


def handler(event,context):
    try:
        expected = fetch_expected_rules()
        actual = get_actual_sg_rules(expected)

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

def clean_instance_name(name):
    # Remove anything in parentheses and strip whitespace
    return re.sub(r'\s*\(.*?\)', '', name).strip()


def normalize_description(desc):
    if not desc:
        return "Unknown"
    return desc.upper().strip()



def fetch_expected_rules():
    github_url = "https://web.git.mil/api/v4/projects/20690/repository/files/PPSM_JSON%2FMCCOG-AWS-SCCA-PPSM.json/raw?ref=Development"
    github_token = ("3aLRUxd-_mXqWrCRYe_C")
    headers = {"PRIVATE-TOKEN": "3aLRUxd-_mXqWrCRYe_C"}


    response = requests.get(github_url, headers=headers)
    response.raise_for_status()
    rules = response.json()


    sg_data = defaultdict(lambda: [[], []])

    for rule in rules:
        low = rule.get('Low Port')
        high = rule.get('High Port')
        protocol = rule.get('IP Protocol', 'Unknown')
        sg_name = rule.get('AWS SCCA Security Group')

        if low is not None and high is not None:
            try:
                low = int(low)
                high = int(high)
            except ValueError:
                continue  # skip if ports are not valid integers
        else:
            continue  # skip if ports are missing

        if not sg_name:
            continue

        instance_names = [clean_instance_name(name) for name in sg_name.split(',')]

        for instance_name in instance_names:
            sg_data[instance_name][0].append([low, high])
            sg_data[instance_name][1].append(protocol)



    return dict(sg_data)

def get_security_group_name(sg):
    tags = sg.get('Tags', [])
    for tag in tags:
        if tag.get('Key') == 'Name':
            return tag.get('Value')
    return sg.get('GroupName')




def get_sg_ids_from_instance_name(instance_name):
    response = ec2.describe_instances(
        Filters=[{
            'Name': 'tag:Name',
            'Values': [instance_name]
        }]
    )
    sg_ids = set()
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            for sg in instance.get('SecurityGroups', []):
                sg_ids.add(sg['GroupId'])
    return list(sg_ids)

def get_actual_sg_rules(expected_rules):
    sg_data = defaultdict(lambda: [[], []])

    for instance_name in expected_rules:
        sg_ids = get_sg_ids_from_instance_name(instance_name)
        if not sg_ids:
            continue

        response = ec2.describe_security_groups(GroupIds=sg_ids)
        for sg in response['SecurityGroups']:
            for rule in sg.get('IpPermissions', []):
                from_port = rule.get('FromPort')
                to_port = rule.get('ToPort')
                proto = normalize_description(rule.get('IpProtocol'))

                if from_port is None or to_port is None:
                    continue

                # Count each source separately
                sources = (
                    rule.get('IpRanges', []) +
                    rule.get('Ipv6Ranges', []) +
                    rule.get('UserIdGroupPairs', []) +
                    rule.get('PrefixListIds', [])
                )
                if not sources:
                    # no specific source, still count the rule
                    sg_data[instance_name][0].append([from_port, to_port])
                    sg_data[instance_name][1].append(proto)
                else:
                    for _ in sources:
                        sg_data[instance_name][0].append([from_port, to_port])
                        sg_data[instance_name][1].append(proto)

    return dict(sg_data)


def compare_rules(expected, actual):
    compliant = []
    non_compliant = []

    for instance_name, expected_data in expected.items():
        expected_ports, expected_protos = expected_data
        actual_data = actual.get(instance_name)

        if not actual_data:
            non_compliant.append(instance_name)
            continue

        actual_ports, actual_protos = actual_data

        expected_pairs = sorted(zip(expected_ports, expected_protos))
        actual_pairs = sorted(zip(actual_ports, actual_protos))

        if expected_pairs == actual_pairs:
            compliant.append(instance_name)
        else:
            non_compliant.append(instance_name)

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

def sync_security_group_rules(desired_rules, allow_deletion=False):
    """
    Syncs rules to a fixed Security Group named 'Auto_sg'.
    
    Args:
        desired_rules: List of dictionaries with keys 'IP Protocol', 'low port', 'high port', and 'IP range'.
        allow_deletion (bool): If True, deletes existing rules not in desired_rules.
    """
    sg_name = "Auto_sg"
    ec2 = boto3.client("ec2")

    # Step 1: Get the security group ID by name
    response = ec2.describe_security_groups(Filters=[{"Name": "group-name", "Values": [sg_name]}])
    if not response["SecurityGroups"]:
        raise Exception(f"Security Group '{sg_name}' not found.")

    sg_id = response["SecurityGroups"][0]["GroupId"]
    current_permissions = response["SecurityGroups"][0].get("IpPermissions", [])

    # Step 2: Build desired permission structure
    new_permissions = []
    for rule in desired_rules:
        proto = rule.get("IP Protocol", "-1")
        from_port = int(rule.get("low port"))
        to_port = int(rule.get("high port"))
        cidr = rule.get("IP range", "0.0.0.0/0")

        new_permissions.append({
            "IpProtocol": proto,
            "FromPort": from_port,
            "ToPort": to_port,
            "IpRanges": [{"CidrIp": cidr}]
        })

    # Step 3: Normalize and compare current vs desired
    def normalize(perms):
        norm = set()
        for p in perms:
            proto = p.get("IpProtocol", "-1")
            from_port = p.get("FromPort", -1)
            to_port = p.get("ToPort", -1)
            cidrs = [r.get("CidrIp") for r in p.get("IpRanges", [])]
            for cidr in cidrs:
                norm.add((proto, from_port, to_port, cidr))
        return norm

    current_rules = normalize(current_permissions)
    desired_rules_set = normalize(new_permissions)

    to_add = desired_rules_set - current_rules
    to_remove = current_rules - desired_rules_set if allow_deletion else set()

    # Step 4: Add missing rules
    if to_add:
        permissions_to_add = []
        for proto, from_p, to_p, cidr in to_add:
            permissions_to_add.append({
                "IpProtocol": proto,
                "FromPort": from_p,
                "ToPort": to_p,
                "IpRanges": [{"CidrIp": cidr}]
            })

        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=permissions_to_add
        )

    # Step 5: Optionally remove rules not in desired
    if allow_deletion and to_remove:
        permissions_to_remove = []
        for proto, from_p, to_p, cidr in to_remove:
            permissions_to_remove.append({
                "IpProtocol": proto,
                "FromPort": from_p,
                "ToPort": to_p,
                "IpRanges": [{"CidrIp": cidr}]
            })

        ec2.revoke_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=permissions_to_remove
        )