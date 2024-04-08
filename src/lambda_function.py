import json
import boto3
import os

sqs = boto3.client('sqs')
sts = boto3.client('sts')

caller = sts.get_caller_identity()
account_number = caller['Account']
session = boto3.session.Session()
aws_region = session.region_name

SQS_NAME=os.environ['environment_varible']    # Replace SQS_NAME value if required

queueUrl = "https://sqs.{0}.amazonaws.com/{1}/{2}".format(aws_region, account_number, SQS_NAME)
print(queueUrl)

def lambda_handler(event, context):
    print(event)
    event = event['body']
    
    response = sqs.send_message(
        QueueUrl=queueUrl,
        DelaySeconds=10,
        MessageBody=event
    )
     
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
     