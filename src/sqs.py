import boto3
from botocore.exceptions import ClientError

client = boto3.client('sqs')

def crate_sqs_queue(queue_name) :

    try:
        response = client.get_queue_url(QueueName=queue_name)
        queue_url = response['QueueUrl']
        print("Queue already exists:", queue_url)
    except ClientError as e:
        if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
            # Queue doesn't exist, create it
            try:
                response = client.create_queue(QueueName=queue_name)
                queue_url = response['QueueUrl']
                print("Queue created:", queue_url)
            except ClientError as e:
                print("Error creating queue:", e)
        else:
            print("Error checking queue existence:", e)


