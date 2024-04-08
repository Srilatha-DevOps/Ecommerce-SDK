import boto3
from botocore.exceptions import ClientError

client = boto3.client('dynamodb')

def crate_dynamodb_table(table_name,partition_key) :

    try:
        response = client.describe_table(TableName=table_name)
        print("Table already exists:", table_name)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            # Table doesn't exist, create it
            try:
                client.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {
                            'AttributeName': partition_key,
                            'KeyType': 'HASH'
                        },
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': partition_key,
                            'AttributeType': 'N'
                        },
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                print("Table created:", table_name)
            except ClientError as e:
                print("Error creating table:", e)
        else:
            print("Error checking table existence:", e)

