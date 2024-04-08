import boto3
import json
from botocore.exceptions import ClientError

client = boto3.client('iam')


def create_lambda_role(role_name, queue_name, sqs_policy_name):

    try:
        response = client.get_role(RoleName=role_name)
        role_arn = response['Role']['Arn']
        print("IAM role already exists:", role_name)

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchEntity':
            # Role doesn't exist, create it
            try:
                response = client.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps({
                        'Version': '2012-10-17',
                        'Statement': [
                            {
                                'Effect': 'Allow',
                                'Principal': {'Service': 'lambda.amazonaws.com'},
                                'Action': 'sts:AssumeRole'
                            }
                        ]
                    })
                )
                role_arn = response['Role']['Arn']
                print("IAM role created:", role_name)
            except ClientError as e:
                print("Error creating role:", e)
        else:
            print("Error checking role existence:", e)


                # Attach predefined policies to the role

    if role_arn:

        policy_exists = None
        
        try:
            client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/AWSLambda_FullAccess'
            )
            print("LambdaFullAccess policy has been attached")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'EntityAlreadyExists':
                print("Permission is already in place")
        
        try:
            client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole'
            )
            print("Lambda ExecutionRole policy has been attached")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'EntityAlreadyExists':
                print("Permission is already in place")

        try:
            client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess'
            )
            print("Lambda ExecutionRole policy has been attached")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'EntityAlreadyExists':
                print("Permission is already in place")

        try:
            client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/AmazonSESFullAccess'
            )
            print("Lambda ExecutionRole policy has been attached")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'EntityAlreadyExists':
                print("Permission is already in place")

        try:
            client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
            )
            print("Lambda ExecutionRole policy has been attached")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'EntityAlreadyExists':
                print("Permission is already in place")

        # Create and attach the custom policy to the role

        try:

            response = client.get_role_policy(
                RoleName=role_name,
                PolicyName=sqs_policy_name
            )


            if response['PolicyName']:
               print('Policy already exists', sqs_policy_name)
               policy_exists = response['PolicyName']
            else:

                response = client.create_policy(
                    PolicyName=sqs_policy_name,
                    PolicyDocument=json.dumps({
                    'Version': '2012-10-17',
                    'Statement': [
                    {
                        'Effect': 'Allow',
                        'Action': 'sqs:SendMessage',
                        'Resource': f'arn:aws:sqs:us-east-1:471112581276:{queue_name}'  # Replace with your SQS queue ARN
                    }]})
                )
                policy_arn = response['Policy']['Arn']
                print("Custom policy created:", sqs_policy_name)

            if not policy_exists and policy_arn:
                try:
                    client.attach_role_policy(
                        RoleName=role_name,
                        PolicyArn=policy_arn
                    )
                    print("Attached custom policy to the role.")
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    if error_code == 'EntityAlreadyExists':
                        print("Permission is already in place")
                    else:
                        print("error in attaching polcy", e)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'EntityAlreadyExists':
                print("Permission is already in place")




def create_ecs_roles(ecs_task_Execution_role_name, ecs_task_role_name, task_role_policy_name):

    #Execution_Role
    try:
        response = client.get_role(RoleName=ecs_task_Execution_role_name)
        role_arn = response['Role']['Arn']
        print("IAM role already exists:", ecs_task_Execution_role_name)

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchEntity':
            # Role doesn't exist, create it
            try:
                response = client.create_role(
                    RoleName=ecs_task_Execution_role_name,
                    AssumeRolePolicyDocument=json.dumps({
                        'Version': '2012-10-17',
                        'Statement': [
                            {
                                'Effect': 'Allow',
                                'Principal': {'Service': 'ecs-tasks.amazonaws.com'},
                                'Action': 'sts:AssumeRole'
                            }
                        ]
                    })
                )
                role_arn = response['Role']['Arn']
                print("IAM role created:", role_arn)
            except ClientError as e:
                    print("Error creating role:", e)
        else:
            print("Error checking role existence:", e)

    # Attach predefined policies to the role
    if role_arn:
        try:
            client.attach_role_policy(
                RoleName=ecs_task_Execution_role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy'
            )
            print("Execution policy policy has been attached")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'EntityAlreadyExists':
                print("Permission is already in place")

            

    #Task Role
    try:
        response = client.get_role(RoleName=ecs_task_role_name)
        role_arn = response['Role']['Arn']
        print("IAM role already exists:", ecs_task_role_name)

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchEntity':
            # Role doesn't exist, create it
            try:
                response = client.create_role(
                    RoleName=ecs_task_role_name,
                    AssumeRolePolicyDocument=json.dumps({
                        'Version': '2012-10-17',
                        'Statement': [
                            {
                                'Effect': 'Allow',
                                'Principal': {'Service': 'ecs-tasks.amazonaws.com'},
                                'Action': 'sts:AssumeRole'
                            }
                        ]
                    })
                )
                role_arn = response['Role']['Arn']
                print("IAM role created:", role_arn)
            except ClientError as e:
                    print("Error creating role:", e)
        else:
            print("Error checking role existence:", e)

                # Create and attach the custom policy to the role
    if role_arn:

        policy_exists = None
        
        try:
            response = client.get_role_policy(
                RoleName=ecs_task_role_name,
                PolicyName=task_role_policy_name
            )


            if response['PolicyName']:
               print('Policy already exists', task_role_policy_name)
               policy_exists = response['PolicyName']
            else:
                
                    response = client.create_policy(
                        PolicyName=task_role_policy_name,
                        PolicyDocument=json.dumps({
                        'Version': '2012-10-17',
                        'Statement': [
                            {
                                'Effect': 'Allow',
                                'Action': [
                                    's3:GetObject',
                                    's3:PutObject',
                                    'dynamodb:GetItem',
                                    'dynamodb:PutItem',
                                    'sqs:ReceiveMessage',
                                    'sqs:GetQueueUrl',
                                    'sqs:GetQueueAttributes',
                                    'sqs:DeleteMessage'
                                ],
                                'Resource': '*'
                            }
                        ]})
                    )
                    policy_arn = response['Policy']['Arn']
                    print("Custom policy created:", task_role_policy_name)
            if not policy_exists and policy_arn:

                try:
                    client.attach_role_policy(
                        RoleName=ecs_task_role_name,
                        PolicyArn=policy_arn
                    )
                    print("Attached custom policy to the role.")
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    if error_code == 'EntityAlreadyExists':
                        print("Permission is already in place")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'EntityAlreadyExists':
                print("Permission is already in place")
        

            