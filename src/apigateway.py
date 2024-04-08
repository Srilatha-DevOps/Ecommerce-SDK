import boto3
from botocore.exceptions import ClientError

# Initialize the API Gateway client
client = boto3.client('apigateway')
lambda_client = boto3.client('lambda')


def create_api(api_name, resource_path, stage_name, lambda_function_name):

    # print('here coming into api')
    api_id = ''

    try:
        response = client.get_rest_apis()
        # print(response)
        for item in response['items']:
            if item['name'] == api_name:
                api_id = item['id']
                print("API already exists:", api_name)
                break
            else:
                api_id = None
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
           api_id = None
    
    if not api_id:

        try:
            response = client.create_rest_api(name=api_name)
            api_id = response['id']
            print(api_id)
            print("API created:", api_name)
        except ClientError as e:
            print("Error creating API:", e)

    if api_id:

        try:
            lambda_client.add_permission(
                FunctionName=lambda_function_name,
                StatementId='apigateway-invoke',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f'arn:aws:execute-api:us-east-1:471112581276:{api_id}/*/*'
            )
            print("Permission added for API Gateway to invoke Lambda")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceConflictException':
                print("Permission is already in place")
            
        # Create Resource
        try:
            response = client.get_resources(restApiId=api_id)
            root_resource_id = next(item for item in response['items'] if item['path'] == '/')
            root_resource_id = root_resource_id['id']

            #Check whether resource exists
            resource_id = ''

            response = client.get_resources(restApiId=api_id)

            if response['items'][1]['path'] == f'/{resource_path}':
               resource_id = response['items'][1]['id']
               print('Resource already exists with path:', resource_path)
            else:
                response = client.create_resource(restApiId=api_id, parentId=root_resource_id, pathPart=resource_path)
                resource_id = response['id']
                print("Resource created:", resource_path)
        except ClientError as e:
            print("Error creating resource:", e)

        if resource_id:
            #check if method exists
            response = client.get_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='POST'
            )

            method = response['httpMethod']

            if response['httpMethod'] == 'POST':
                print('Method already exists', method)
            # Create POST method
            else:

                try:
                    response = client.put_method(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='POST',
                        authorizationType='NONE'
                    )
                    method = response['httpMethod']
                    print("Method created:", 'POST')
                except ClientError as e:
                    print("Error creating method:", e)

        if method:
            
            integration = ''
            try:
                response = client.get_integration(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod=method
                )
                integration = response['uri']
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceNotFoundException':
                   integration = None
            

            if integration:
                print('Integration already exists', integration)
            else:

                # Create integration
                try:
                    response = lambda_client.get_function(FunctionName=lambda_function_name)
                    lambda_arn = f"arn:aws:lambda:{response['Configuration']['FunctionArn'].split(':')[3]}:{response['Configuration']['FunctionArn'].split(':')[4]}:function:{lambda_function_name}"
                    invoke_uri = f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
                    print("Invoke URI (ARN) for Lambda function:", invoke_uri)

                    response = client.put_integration(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='POST',
                        type='AWS_PROXY',
                        integrationHttpMethod='POST',
                        uri=invoke_uri
                    )
                    integration = response['uri']
                    print("Integration created for method POST", integration)
                except ClientError as e:
                    print("Error creating integration:", e)
                

        if integration:
            
            deployment_id = ''
            try:
                # Check if the deployment already exists
                response = client.get_deployments(restApiId=api_id)
                # print(response)
                
                if response['items']:
                    deployment_id = response['items'][0]['id']
                    # print('deployment already exists', deployment_id)
                else:
                    deployment_id = None
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceNotFoundException':
                   deployment_id = None


            if deployment_id:
                print('deployment already exists', deployment_id)
            else:

                try:
                    response = client.create_deployment(restApiId=api_id, stageName=stage_name)
                    deployment_id = response['id']
                    print("Deployment created for stage:", stage_name)
                except ClientError as e:
                    print("Error creating deployment:", e)

    else:
        print('api already exists')

            