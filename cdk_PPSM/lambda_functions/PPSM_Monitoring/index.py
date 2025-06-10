import requests
import json 
import boto3
from collections import defaultdict



PPSM_JSON = "https://raw.githubusercontent.com/niko456gt/AWS/refs/heads/main/cdk_PPSM/PPSM_Rules/rules.json"
def fetch_rules(url):

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    return data

def extract_security_group_rules(rules):
    sg_data = defaultdict(list)
    for rule in rules:
        low = rule.get('low port',0)
        high = rule.get('high port',0)
        protocol = rule.get('IP Protocol','Unknown')
        security_groups = rule.get('Security Group')

        if security_groups:
            sg_data[security_groups].append([[low, high],[protocol]])

    return sg_data






def handler(event,context):
    try: 
        rules = fetch_rules(PPSM_JSON)
        results = extract_security_group_rules(rules)
        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }
    except Exception as e:
        print(f"Error processing rules: {e}")
        return {
            'statusCode': 500,
            'body': f"Failed bcs:{str(e)}"
        }