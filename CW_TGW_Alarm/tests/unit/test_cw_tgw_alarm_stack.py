import aws_cdk as core
import aws_cdk.assertions as assertions

from cw_tgw_alarm.cw_tgw_alarm_stack import CwTgwAlarmStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cw_tgw_alarm/cw_tgw_alarm_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CwTgwAlarmStack(app, "cw-tgw-alarm")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
