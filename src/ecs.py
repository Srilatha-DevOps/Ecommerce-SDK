import boto3
from botocore.exceptions import ClientError

# Initialize the ECS client
client = boto3.client('ecs')
vpc_client = boto3.client('ec2')


def create_ecs(cluster_name, task_definition_family, service_name, vpc_name, image_uri):
    
    cluster_arn = None
    # Check if the ECS cluster already exists
    try:
        response = client.describe_clusters(clusters=[cluster_name])
        if response['clusters']:
            cluster_arn = response['clusters'][0]['clusterArn']
            print(cluster_arn)
            print("ECS cluster already exists:", cluster_name)
        else:
            cluster_arn = None
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            cluster_arn = None

    if not cluster_arn:
        # Create the ECS cluster
        try:
            response = client.create_cluster(clusterName=cluster_name)
            cluster_arn = response['cluster']['clusterArn']
            print("ECS cluster created:", cluster_name)
        except ClientError as e:
            print("Error creating ECS cluster:", e)

    if cluster_arn:

        task_definition_arn = ''
        # Define your container definitions for the task definition
        container_definitions = [
            {
                'name': 'my-container',
                'image': image_uri,
                'cpu': 256,
                'memory': 512,
                'essential': True,
                'environment': [
                {
                    'name': 'S3_BUCKET', 
                    'value': 'my-ecommerce-bucket-1345'
                },
                {
                    'name': 'DYNAMODB_TABLE', 
                    'value': 'my-table'
                },
                {
                    'name': 'SQS_QRL', 
                    'value': 'https://sqs.us-east-1.amazonaws.com/471112581276/my-queue'
                }
                ],
                'logConfiguration': {
                'logDriver': 'awslogs',
                'options': {
                    'awslogs-group': 'ecommerce-loggroup',
                    'awslogs-region': 'us-east-1',
                    'awslogs-stream-prefix': 'ecs'
                }
                }
            }
            # Add more container definitions as needed
        ]

        # Register the task definition
        try:
            response = client.register_task_definition(
                family=task_definition_family,
                containerDefinitions=container_definitions,
                taskRoleArn='arn:aws:iam::471112581276:role/ecs-task-role',
                executionRoleArn='arn:aws:iam::471112581276:role/ecs-execution-role',
                cpu='256',
                memory='512',
                networkMode='awsvpc',
                requiresCompatibilities=['FARGATE']
            )
            task_definition_arn = response['taskDefinition']['taskDefinitionArn']
            print("Task definition created:", task_definition_family)
        except ClientError as e:
            print("Error registering task definition:", e)

        if task_definition_arn:

            #check if Service exists
            service = ''
            try:
                response = client.describe_services(cluster=cluster_name,services=[service_name])
                if response['services']:
                    service = response['services'][0]['serviceName']
                else:
                    service = None
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceNotFoundException':
                    service = None
            # Create the ECS service

            if service:
                print('Service already exists', service)
            else: 
                try:

                    existing_vpcs = vpc_client.describe_vpcs(
                        Filters=[{'Name': 'tag:Name', 'Values': [vpc_name]}]
                    )['Vpcs']
                    if existing_vpcs[0]['VpcId']:
                        vpc_id = existing_vpcs[0]['VpcId']

                    response = vpc_client.describe_security_groups(
                        Filters=[{'Name': 'group-name', 'Values': ['default']},{'Name': 'vpc-id','Values': [vpc_id]}])
                    
                    sg_id = response['SecurityGroups'][0]['GroupId']

                    subnet_ids = []

                    # Check if the subnet already exists
                    existing_subnets = vpc_client.describe_subnets(
                        Filters=[
                            {'Name': 'vpc-id', 'Values': [vpc_id]}
                        ]
                    )['Subnets']    

                    if existing_subnets:
                        for n in range(len(existing_subnets)):
                            subnet_ids.append(existing_subnets[n]['SubnetId'])

                    response = client.create_service(
                        cluster=cluster_name,
                        serviceName=service_name,
                        taskDefinition=task_definition_arn,
                        desiredCount=1,
                        launchType='FARGATE',
                        networkConfiguration={
                            'awsvpcConfiguration': {
                                'subnets': subnet_ids,  # Replace with your subnet IDs
                                'securityGroups': [sg_id],  # Replace with your security group ID
                            }
                        }
                    )
                    print("ECS service created:", service_name)
                except ClientError as e:
                    print("Error creating ECS service:", e)