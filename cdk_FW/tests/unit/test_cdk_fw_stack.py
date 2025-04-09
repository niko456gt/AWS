import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_fw.cdk_fw_stack import CdkFwStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_fw/cdk_fw_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkFwStack(app, "cdk-fw")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
