
aws_region = 'us-east-1'
vpc_name = 'main_vpc'
vpc_cidr_block = '10.0.0.0/16'
subnets = {
    'subnet1': {
        'name': 'subnet-a',
        'cidr': '10.0.1.0/24',
        'az': 'us-east-1a'
    },
    'subent2': {
        'name': 'subnet-b',
        'cidr': '10.0.2.0/24',
        'az': 'us-east-1b'
    }
}
igw_name = 'my-igw'
rw_name = 'my-rgw'
queue_name='my-queue'
bucket_name='my-ecommerce-bucket-1345'
table_name='my-table'
partition_key='id'
lambda_role_name = 'my-lambda-role'
sqs_policy_name = 'my-sqs-policy-name'
ecs_exec_role_name = 'ecs-execution-role'
ecs_task_role_name = 'ecs-task-role' 
task_role_policy_name = 'task-role-policy-to-access-s3-synamodb'
orderprocess_function_name = 'orderprcessing_lambda'
email_lambda_name = 'email_lambda'
api_name = 'my-api'
resource_path = 'checkout'
stage_name = 'dev'
cluster_name = 'my-cluster'
td_name = 'my-task-def'
service_name = 'my-service'
image_uri = '<account>.dkr.ecr.us-east-1.amazonaws.com/ecommerce-repo:latest'