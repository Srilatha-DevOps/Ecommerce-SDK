import boto3

client = boto3.client('ecr')

def crate_ecr_repo(ecr_repo_name) :

    repository = None
    try:
        response = client.describe_repositories(repositoryNames=[ecr_repo_name])
        if response['repositories']:
           repository = response['repositories'][0]['repositoryName']
           print('repository already exists', repository)
    except client.exceptions.RepositoryNotFoundException:
        repository = None

    # Create the ECR repository if it doesn't exist
    if not repository:
        response = client.create_repository(repositoryName=ecr_repo_name)
        return response['repository']

