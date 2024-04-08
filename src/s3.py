import boto3
from botocore.exceptions import ClientError

client = boto3.client('s3')

def crate_s3_bucket(bucket_name) :

    try:
        response = client.head_bucket(Bucket=bucket_name)
        print("Bucket already exists:", bucket_name)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            # Bucket doesn't exist, create it
            try:
                response = client.create_bucket(Bucket=bucket_name)
                print("Bucket created:", bucket_name)
            except ClientError as e:
                print("Error creating bucket:", e)
        else:
            print("Error checking bucket existence:", e)

