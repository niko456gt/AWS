import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_dynamodb.cdk_dynamodb_stack import CdkDynamodbStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_dynamodb/cdk_dynamodb_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkDynamodbStack(app, "cdk-dynamodb")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
