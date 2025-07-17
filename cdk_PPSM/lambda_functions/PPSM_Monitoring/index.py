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
    sync_security_group_rules(rules, allow_deletion=True)


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

    response = requests.get(github_url)
    response.raise_for_status()
    rules = response.json()


    # Now tracking: ports, protocols, and IP ranges
    sg_data = defaultdict(lambda: [[], [], []])  # ports, protocols, CIDRs

    for rule in rules:
        low = rule.get('low port')
        high = rule.get('high port')
        protocol = rule.get('IP Protocol', 'Unknown')
        sg_name = rule.get('Security Group')
        cidr = rule.get('IP range', '0.0.0.0/0')

        if low is not None and high is not None:
            try:
                low = int(low)
                high = int(high)
            except ValueError:
                continue  # skip invalid port values
        else:
            continue  # skip rules without both ports

        if not sg_name:
            continue

        instance_names = [clean_instance_name(name) for name in sg_name.split(',')]

        for instance_name in instance_names:
            sg_data[instance_name][0].append([low, high])
            sg_data[instance_name][1].append(protocol)
            sg_data[instance_name][2].append(cidr)


    return dict(sg_data)

def get_security_group_name(sg):
    tags = sg.get('Tags', [])
    for tag in tags:
        if tag.get('Key') == 'Name':
            return tag.get('Value')
    return sg.get('GroupName')




def get_actual_sg_rules():
    github_url = "https://raw.githubusercontent.com/niko456gt/AWS/refs/heads/main/cdk_PPSM/PPSM_Rules/rules.json"

    sg_data = defaultdict(lambda: [[], [], []])  # ports, protocols, cidrs

    response = ec2.describe_security_groups()

    for sg in response['SecurityGroups']:
        sg_name = sg.get('GroupName', 'UnnamedSG')

        for rule in sg.get('IpPermissions', []):
            from_port = rule.get('FromPort')
            to_port = rule.get('ToPort')
            proto = normalize_description(rule.get('IpProtocol'))

            if from_port is None or to_port is None:
                continue

            # Collect all CIDRs (IPv4 + IPv6)
            cidrs = [r.get('CidrIp') for r in rule.get('IpRanges', [])]
            cidrs += [r.get('CidrIpv6') for r in rule.get('Ipv6Ranges', [])]

            if not cidrs:
                # If no explicit source, default to all (for parity)
                sg_data[sg_name][0].append([from_port, to_port])
                sg_data[sg_name][1].append(proto)
                sg_data[sg_name][2].append("0.0.0.0/0")
            else:
                for cidr in cidrs:
                    sg_data[sg_name][0].append([from_port, to_port])
                    sg_data[sg_name][1].append(proto)
                    sg_data[sg_name][2].append(cidr)

    return dict(sg_data)


def compare_rules(expected, actual):
    compliant = []
    non_compliant = []

    for sg_name, expected_data in expected.items():
        expected_ports, expected_protos, expected_cidrs = expected_data
        actual_data = actual.get(sg_name)

        if not actual_data:
            non_compliant.append(sg_name)
            continue

        actual_ports, actual_protos, actual_cidrs = actual_data

        expected_rules = sorted(zip(expected_ports, expected_protos, expected_cidrs))
        actual_rules = sorted(zip(actual_ports, actual_protos, actual_cidrs))

        if expected_rules == actual_rules:
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
    sg_name = "auto_sg"

    # Fetch SG ID
    response = ec2.describe_security_groups(Filters=[{"Name": "group-name", "Values": [sg_name]}])
    if not response["SecurityGroups"]:
        raise Exception(f"Security Group '{sg_name}' not found.")
    sg_id = response["SecurityGroups"][0]["GroupId"]
    current_permissions = response["SecurityGroups"][0].get("IpPermissions", [])

    # --- Normalize current rules from AWS ---
    def normalize_aws_permissions(perms):
        normalized = set()
        for p in perms:
            proto = p.get("IpProtocol", "-1").lower()
            from_port = p.get("FromPort", -1)
            to_port = p.get("ToPort", -1)

            # IPv4
            for r in p.get("IpRanges", []):
                cidr = r.get("CidrIp", "0.0.0.0/0")
                normalized.add((proto, int(from_port), int(to_port), cidr))

            # IPv6
            for r in p.get("Ipv6Ranges", []):
                cidr = r.get("CidrIpv6", "::/0")
                normalized.add((proto, int(from_port), int(to_port), cidr))
        return normalized

    # --- Normalize desired rules from JSON ---
    def normalize_desired_rules(rules):
        normalized = set()
        for rule in rules:
            proto = rule.get("IP Protocol", "-1").lower()
            from_port = int(rule.get("low port", -1))
            to_port = int(rule.get("high port", -1))
            cidr = rule.get("IP range", "0.0.0.0/0")
            normalized.add((proto, from_port, to_port, cidr))
        return normalized

    current_set = normalize_aws_permissions(current_permissions)
    desired_set = normalize_desired_rules(desired_rules)

    to_add = desired_set - current_set
    to_remove = current_set - desired_set if allow_deletion else set()

    # Add rules
    if to_add:
        permissions_to_add = []
        for proto, from_p, to_p, cidr in to_add:
            ip_key = "CidrIp" if ":" not in cidr else "CidrIpv6"
            perm = {
                "IpProtocol": proto,
                "FromPort": from_p,
                "ToPort": to_p,
                "IpRanges" if ip_key == "CidrIp" else "Ipv6Ranges": [{ip_key: cidr}]
            }
            permissions_to_add.append(perm)

        try:
            ec2.authorize_security_group_ingress(GroupId=sg_id, IpPermissions=permissions_to_add)
            print(f"✅ Added {len(permissions_to_add)} new rule(s) to '{sg_name}'")
        except botocore.exceptions.ClientError as e:
            if "InvalidPermission.Duplicate" in str(e):
                print("⚠️ Some rules already exist. Skipping.")
            else:
                raise

    else:
        print("✅ No new rules to add.")

    # Remove old rules
    if allow_deletion and to_remove:
        permissions_to_remove = []
        for proto, from_p, to_p, cidr in to_remove:
            ip_key = "CidrIp" if ":" not in cidr else "CidrIpv6"
            perm = {
                "IpProtocol": proto,
                "FromPort": from_p,
                "ToPort": to_p,
                "IpRanges" if ip_key == "CidrIp" else "Ipv6Ranges": [{ip_key: cidr}]
            }
            permissions_to_remove.append(perm)

        try:
            ec2.revoke_security_group_ingress(GroupId=sg_id, IpPermissions=permissions_to_remove)
            print(f"🧹 Removed {len(permissions_to_remove)} outdated rule(s) from '{sg_name}'")
        except botocore.exceptions.ClientError as e:
            print(f"⚠️ Failed to remove some rules: {e}")
    else:
        print("🟰 No rules removed.")