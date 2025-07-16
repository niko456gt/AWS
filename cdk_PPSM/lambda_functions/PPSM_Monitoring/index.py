import requests
import json 
import boto3
from collections import defaultdict
import re
import ipaddress
import botocore.exceptions


ec2 = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')


def handler(event,context):
    github_url = "https://raw.githubusercontent.com/niko456gt/AWS/refs/heads/main/cdk_PPSM/PPSM_Rules/rules.json"
    response = requests.get(github_url)
    response.raise_for_status()
    rules = response.json()
    sync_security_group_rules(rules, allow_deletion=False)


    try:
        expected = fetch_expected_rules()
        actual = get_actual_sg_rules()

        compliant, non_compliant = compare_rules(expected, actual)

        publish_metrics_to_cloudwatch(len(compliant), len(non_compliant))
        print("✅ Compliant Security Groups:")
        for sg in compliant:
            print(f"  - {sg}")

        print("\n⚠️ Non-Compliant Security Groups:")
        for sg in non_compliant:
            print(f"  - {sg}")

        print("\n📦 Expected Rules:")
        for sg, rules in expected.items():
            print(f"  - {sg}: {rules}")

        print("\n🔍 Actual Rules:")
        for sg, rules in actual.items():
            print(f"  - {sg}: {rules}")
        return {
            "statusCode": 200,
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
    github_url = "https://raw.githubusercontent.com/niko456gt/AWS/refs/heads/main/cdk_PPSM/PPSM_Rules/rules.json"
    github_token = ("3aLRUxd-_mXqWrCRYe_C")
    headers = {"PRIVATE-TOKEN": "3aLRUxd-_mXqWrCRYe_C"}

    response = requests.get(github_url)
    response.raise_for_status()
    rules = response.json()


    sg_data = defaultdict(lambda: [[], []])

    for rule in rules:
        low = rule.get('low port')
        high = rule.get('high port')
        protocol = rule.get('IP Protocol', 'Unknown')
        sg_name = rule.get('Security Group')

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




def get_actual_sg_rules():
    sg_data = defaultdict(lambda: [[], []])

    response = ec2.describe_security_groups()

    for sg in response['SecurityGroups']:
        sg_name = sg.get('GroupName', 'UnnamedSG')

        for rule in sg.get('IpPermissions', []):
            from_port = rule.get('FromPort')
            to_port = rule.get('ToPort')
            proto = normalize_description(rule.get('IpProtocol'))

            if from_port is None or to_port is None:
                continue

            # Handle all rule sources (IPv4, IPv6, SGs, PrefixLists)
            sources = (
                rule.get('IpRanges', []) +
                rule.get('Ipv6Ranges', []) +
                rule.get('UserIdGroupPairs', []) +
                rule.get('PrefixListIds', [])
            )

            if not sources:
                sg_data[sg_name][0].append([from_port, to_port])
                sg_data[sg_name][1].append(proto)
            else:
                for _ in sources:
                    sg_data[sg_name][0].append([from_port, to_port])
                    sg_data[sg_name][1].append(proto)

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



    """



    Implementing enforcement initial approach

    Syncs rules to a fixed Security Group named 'Auto_sg'.



"""
def normalize_cidr(ip_str):

    try:
        ip = ipaddress.ip_network(ip_str, strict=True)
        return str(ip)
    except ValueError:
        raise ValueError(f"Invalid IP or CIDR format: {ip_str}")


def sync_security_group_rules(desired_rules, allow_deletion=False):
    ec2 = boto3.client("ec2")
    sg_name = "auto_sg"

    # Step 1: Get the security group ID
    response = ec2.describe_security_groups(Filters=[{"Name": "group-name", "Values": [sg_name]}])
    if not response["SecurityGroups"]:
        raise Exception(f"Security Group '{sg_name}' not found.")
    
    sg_id = response["SecurityGroups"][0]["GroupId"]
    current_permissions = response["SecurityGroups"][0].get("IpPermissions", [])

    # Step 2: Build desired permission structure (and normalize)
    desired_permissions = []
    for rule in desired_rules:
        proto = str(rule.get("IP Protocol", "-1")).lower().strip()
        from_port = int(rule.get("low port"))
        to_port = int(rule.get("high port"))
        cidr = rule.get("IP range", "0.0.0.0/0").strip()

        desired_permissions.append({
            "IpProtocol": proto,
            "FromPort": from_port,
            "ToPort": to_port,
            "IpRanges": [{"CidrIp": cidr}]
        })

    # Step 3: Normalize both current and desired rules
    def normalize(perms):
        norm = set()
        for p in perms:
            proto = str(p.get("IpProtocol", "-1")).lower().strip()
            from_port = p.get("FromPort", -1)
            to_port = p.get("ToPort", -1)

            for r in p.get("IpRanges", []):
                cidr = r.get("CidrIp", "0.0.0.0/0").strip()
                norm.add((proto, from_port, to_port, cidr))
        return norm

    current_rules_set = normalize(current_permissions)
    desired_rules_set = normalize(desired_permissions)

    to_add = desired_rules_set - current_rules_set
    to_remove = current_rules_set - desired_rules_set if allow_deletion else set()

    print("---- CURRENT RULES ----")
    for r in current_rules_set:
        print(r)

    print("---- DESIRED RULES ----")
    for r in desired_rules_set:
        print(r)

    print("---- RULES TO ADD ----")
    for r in to_add:
        print(r)

    print("---- RULES TO REMOVE ----")
    for r in to_remove:
        print(r)

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

        try:
            ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=permissions_to_add
            )
            print(f"✅ Added {len(permissions_to_add)} rule(s) to {sg_name}")
        except botocore.exceptions.ClientError as e:
            if "InvalidPermission.Duplicate" in str(e):
                print("⚠️ Some rules already exist. Skipping duplicates.⚠️")
            else:
                raise

    # Step 5: Optionally remove extra rules
    if allow_deletion and to_remove:
        permissions_to_remove = []
        for proto, from_p, to_p, cidr in to_remove:
            permissions_to_remove.append({
                "IpProtocol": proto,
                "FromPort": from_p,
                "ToPort": to_p,
                "IpRanges": [{"CidrIp": cidr}]
            })

        try:
            ec2.revoke_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=permissions_to_remove
            )
            print(f"❌ Removed {len(permissions_to_remove)} rule(s) from {sg_name}")
        except botocore.exceptions.ClientError as e:
            print(f"⚠️ Failed to remove some rules: {e}")