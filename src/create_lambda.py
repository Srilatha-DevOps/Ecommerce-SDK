import boto3
import zipfile
import json
from botocore.exceptions import ClientError

client = boto3.client('lambda')
iam = boto3.client('iam')
s3 = boto3.client('s3')

def create_orderprocessing_lambda(function_name, queue_name, role_name):

    try:
        response = client.get_function(FunctionName=function_name)
        print("Lambda function already exists:", function_name)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            # Lambda function doesn't exist, create it
            try:

                response = iam.get_role(
                    RoleName=role_name
                )

                role_arn = response['Role']['Arn']

                if role_arn:

                    # Create a ZIP file containing the Lambda function code
                    with zipfile.ZipFile('./orderprocessor_function.zip', 'w') as zf:
                        zf.write('lambda_function.py')  # Add your Lambda function Python file to the ZIP

                    # Upload the ZIP file to Lambda and create the function
                    with open('./orderprocessor_function.zip', 'rb') as zf:
                        response = client.create_function(
                            FunctionName=function_name,
                            Runtime='python3.8',
                            Role=role_arn,  # Replace with your Lambda execution role ARN
                            Handler='lambda_function.lambda_handler',
                            Code={'ZipFile': zf.read()},
                            Environment={'Variables': {
                                'environment_varible': queue_name  # Replace with your desired environment variable key-value pair
                            }}
                        )
                        print("Lambda function created:", function_name)
            except ClientError as e:
                print("Error creating Lambda function:", e)
        else:
            print("Error checking Lambda function existence:", e)


def create_email_lambda(function_name, role_name, table_name, bucket_name):

    try:
        response = client.get_function(FunctionName=function_name)
        function_arn = response['Configuration']['FunctionArn']
        print(function_arn)
        print("Lambda function already exists:", function_name)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            # Lambda function doesn't exist, create it
            try:

                response = iam.get_role(
                    RoleName=role_name
                )

                role_arn = response['Role']['Arn']

            except ClientError as e:
                print("Error creating Lambda function:", e)

            if role_arn:

                with open('./email.zip', 'rb') as zf:
                    response = client.create_function(
                        FunctionName=function_name,
                        Runtime='python3.8',
                        Role=role_arn,  # Replace with your Lambda execution role ARN
                        Handler='email.lambda_handler',
                        Code={'ZipFile': zf.read()},
                        Environment={'Variables': {
                            'environment_varible': table_name  # Replace with your desired environment variable key-value pair
                        }}
                    )
                    function_arn = response['FunctionArn']
                    print(function_arn)
                    print("Lambda function created:", function_name)
        
        else:
            print("Error checking Lambda function existence:", e)

    if function_arn:

        try:
            client.add_permission(
                FunctionName=function_arn,
                StatementId='send-email',
                Action='lambda:*',
                Principal='s3.amazonaws.com',
                SourceArn=f'arn:aws:s3:::{bucket_name}/*'
            )
            print("Permission added for s3 to invoke Lambda")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceConflictException':
                print("Permission is already in place")
            else:
                print('error creating permission', e)

        try:
            response = s3.put_bucket_notification_configuration(
                Bucket=bucket_name,
                NotificationConfiguration={
                    'LambdaFunctionConfigurations': [
                            {
                                'LambdaFunctionArn': function_arn,
                                'Events': ['s3:ObjectCreated:*']
                            }
                        ]
                }
            )
        except ClientError as e:
            print('unable to create S3 trigger', e)
                    
        
                