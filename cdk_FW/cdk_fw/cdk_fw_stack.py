from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_networkfirewall as fw,
    CfnOutput
)
from aws_cdk import App, Environment
from constructs import Construct

class CdkFwStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # ---------------------------------------------------------------------
        # Network Firewall Resources
        # ---------------------------------------------------------------------
        # Ask for the VPC ID from the user
        # stateless firewall rules
        # ----------------- --------------------------------------------------- 



        stateless_rule_group = fw.CfnRuleGroup(self, "StatelessRuleGroup",
            capacity=100,
            rule_group_name="MyStatelessRuleGroup",
            type="STATELESS",
            rule_group={
                "rulesSource": {
                    "statelessRulesAndCustomActions": {
                        "statelessRules": [
                            {
                                "priority": 1,
                                "ruleDefinition": {
                                    "actions": ["aws:pass"],
                                    "matchAttributes": {
                                        "sources": [{"addressDefinition": "10.0.0.0/8"}],
                                        "destinations": [{"addressDefinition": "0.0.0.0/0"}],
                                        "protocols": [6],  # TCP
                                    },
                                },
                            }
                        ]
                    }
                }
            }
        )

        vpc_id = "vpc-088ed51f8070c36c6"
        vpc = ec2.Vpc.from_lookup(self, "WebAppVPC", vpc_id=vpc_id)
        # ---------------------------------------------------------------------
        # Network Firewall Rule Group (Stateful)
        # ---------------------------------------------------------------------
        stateful_rule_group = fw.CfnRuleGroup(
            self,
            "StatefulRuleGroup",
            capacity=5,             # Adjust capacity as needed
            rule_group_name="myfirstrulegroup",
            type="STATEFUL",
            description="Allow any traffic",
            rule_group=fw.CfnRuleGroup.RuleGroupProperty(
                rules_source=fw.CfnRuleGroup.RulesSourceProperty(
                    rules_string="pass tcp any any -> any any (msg:\"Allow any traffic\"; flow; established,related; sid:1; rev:1;)"
                    # You can also use rules_source_list for more complex stateful rules
                ),
                stateful_rule_options=fw.CfnRuleGroup.StatefulRuleOptionsProperty(
                    rule_order="DEFAULT_ACTION_ORDER"
                )
            ),
        )

        # ---------------------------------------------------------------------
        # Network Firewall Policy
        # ---------------------------------------------------------------------
        firewall_policy = fw.CfnFirewallPolicy(
            self,
            "FirewallPolicy",
            firewall_policy_name="MyFirewallPolicy",
            firewall_policy=fw.CfnFirewallPolicy.FirewallPolicyProperty(
                stateless_default_actions=["aws:pass"],
                stateless_fragment_default_actions=["aws:pass"],
                stateful_default_actions=["aws:drop"],
                stateful_engine_options=fw.CfnFirewallPolicy.StatefulEngineOptionsProperty(
                    rule_order="DEFAULT_ACTION_ORDER"
                ),
                stateful_rule_group_references=[
                    fw.CfnFirewallPolicy.StatefulRuleGroupReferenceProperty(
                        priority=10,
                        resource_arn=stateful_rule_group.attr_rule_group_arn
                    )
                ]
            ),
            description="My Network Firewall Policy"
        )

        # ---------------------------------------------------------------------
        # Create the Network Firewall
        # ---------------------------------------------------------------------
        subnet_ids = [subnet.subnet_id for subnet in vpc.private_subnets]  # Deploy in private subnets

        network_firewall = fw.CfnFirewall(
            self,
            "NetworkFirewall",
            firewall_policy_arn=firewall_policy.attr_firewall_policy_arn,
            subnet_mappings=[
                fw.CfnFirewall.SubnetMappingProperty(
                    subnet_id=subnet_id
                ) for subnet_id in subnet_ids
            ],
            vpc_id=vpc.vpc_id,
            firewall_name="my-network-firewall",
            description="My Network Firewall"
        )

        # Output the Firewall ARN
        CfnOutput(self, "FirewallArn", value=network_firewall.attr_firewall_arn)



