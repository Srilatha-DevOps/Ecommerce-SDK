import variables
import vpc, sqs, s3, dynamodb, iam, create_lambda, apigateway, ecs




#create_vpc
vpc.crate_vpc(variables.vpc_name, variables.vpc_cidr_block, variables.subnets, variables.igw_name)

#Crate SQS queue
sqs.crate_sqs_queue(variables.queue_name)

#Create S3 bucket
s3.crate_s3_bucket(variables.bucket_name)

#Create dynamodb table
dynamodb.crate_dynamodb_table(variables.table_name, variables.partition_key)

#Create IAM Roles
iam.create_lambda_role(variables.lambda_role_name, variables.queue_name, variables.sqs_policy_name)
iam.create_ecs_roles(variables.ecs_exec_role_name, variables.ecs_task_role_name, variables.task_role_policy_name)

#Create Lambda function
create_lambda.create_orderprocessing_lambda(variables.orderprocess_function_name, variables.queue_name, variables.lambda_role_name)

#Create API gateway
apigateway.create_api(variables.api_name, variables.resource_path, variables.stage_name, variables.orderprocess_function_name)

#Create ECS cluster
ecs.create_ecs(variables.cluster_name, variables.td_name, variables.service_name, variables.vpc_name, variables.image_uri)

#Create Email Lambda
create_lambda.create_email_lambda(variables.email_lambda_name, variables.lambda_role_name, variables.table_name, variables.bucket_name)


