from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3 as s3,
    aws_ssm as ssm,
    aws_backup as bk,
    aws_events as events,)


class WebAppStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, vpc_id,subnet_ids, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

       # Ask for the VPC ID from the user
        if not vpc_id:
            raise ValueError("VPC ID must be provided")
        vpc = ec2.Vpc.from_lookup(self, "WebAppVPC", vpc_id=vpc_id)
            # Use the provided VPC ID to retrieve the VPC
        #lookup for subnet id
        if not subnet_ids:
            raise ValueError("Subnet ID must be provided")
        subnet_ids = ec2.SubnetSelection(one_per_az=True, subnet_type=ec2.SubnetType.PUBLIC)
        # Create a security group for the EC2 instance
        sg = ec2.SecurityGroup(self, "WebAppSG",
                               vpc=vpc,
                               description="Allow HTTP and SSH traffic",
                               allow_all_outbound=True)

        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP traffic")
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "Allow SSH traffic")

        # Create an IAM role for the EC2 instance
        role = iam.Role(self, "WebAppRole",
                        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
                        managed_policies=[
                            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                            
                        ])


        # Create an EC2 instance for the web application
        instance = ec2.Instance(self, "WebAppInstance",
                                instance_type=ec2.InstanceType("t2.micro"),
                                machine_image=ec2.MachineImage.latest_amazon_linux2(),
                                vpc=vpc,
                                vpc_subnets=subnet_ids,
                                security_group=sg,
                                role=role)

        # Add user data to install a web server and copy files from S3 bucket
        instance.user_data.add_commands(
                    "sudo yum update -y",
                    "sudo amazon-linux-extras install -y lamp-mariadb10.2-php7.2 php7.2",
                    "sudo yum install -y httpd",
                    "sudo systemctl start httpd",
                    "sudo systemctl enable httpd",
                    'echo "<h1>Hello from AWS EC2 with Apache!</h1>" | sudo tee /var/www/html/index.html',
        )
        #Output the public IP address of the EC2 instance
        cdk.CfnOutput(self, "WebAppPublicIP", value=instance.instance_public_ip)
        cdk.CfnOutput(self, "endpoint", value=instance.instance_public_dns_name)