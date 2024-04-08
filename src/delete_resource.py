import boto3

#ECR 

client = boto3.client('ecr')

client.delete_resource(
    TypeName='AWS::ECR::Repository',
    Identifier='ecommerce-repo'
)