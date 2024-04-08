import boto3
from botocore.exceptions import ClientError

client = boto3.client('ec2')

def crate_vpc(name, 
              vpc_cidr_block,
              subnets,
              igw_name 
    ):

    existing_vpcs = client.describe_vpcs(
        Filters=[{'Name': 'tag:Name', 'Values': [name]}]
    )['Vpcs']
    if existing_vpcs[0]['VpcId']:
        print(f"VPC with name '{name}' already exists.")
        vpc_id = existing_vpcs[0]['VpcId']
    else:
        vpc_id = None



    if not vpc_id:
        # Create the VPC
        response = client.create_vpc(CidrBlock=vpc_cidr_block)
        vpc_id = response['Vpc']['VpcId']
        print("VPC created:", vpc_id)

        # Add a name tag to the VPC
        client.create_tags(Resources=[vpc_id], Tags=[{'Key': 'Name', 'Value': name}])
        
        if vpc_id:
            client.modify_vpc_attribute(
                VpcId=vpc_id,
                EnableDnsSupport={'Value': True}
            )  
            
            client.modify_vpc_attribute(
                VpcId=vpc_id,
                EnableDnsHostnames={'Value': True}
            )

    if vpc_id:
        
    # Create or check existing subnets for the VPC
        subnet_ids = []
        for map_data in subnets.values():


            # Check if the subnet already exists
            existing_subnets = client.describe_subnets(
                Filters=[
                    {'Name': 'vpc-id', 'Values': [vpc_id]},
                    {'Name': 'cidrBlock', 'Values': [map_data['cidr']]}
                ]
            )['Subnets']    

            if existing_subnets:
                for n in range(len(existing_subnets)):
                    subnet_ids.append(existing_subnets[n]['SubnetId'])
                print(f"Subnet '{map_data['name']}' with CIDR '{map_data['cidr']}' already exists in VPC '{vpc_id}'.")
            else:
                # Create the subnet
                response = client.create_subnet(
                    VpcId=vpc_id,
                    CidrBlock=map_data['cidr'],
                    AvailabilityZone=map_data['az']
                )
                subnet_id = response['Subnet']['SubnetId']
                subnet_ids.append(response['Subnet']['SubnetId'])
                print(f"Subnet '{map_data['name']}' created with ID '{subnet_id}'.")

                # Add a name tag to the subnet
                client.create_tags(Resources=[subnet_id], Tags=[{'Key': 'Name', 'Value': map_data['name']}])


# ## Create IGW
    if vpc_id:
    
        existing_igws = client.describe_internet_gateways(
        Filters=[{'Name': 'tag:Name', 'Values': [igw_name]}]
            )['InternetGateways']
        
        if existing_igws:
            print(f"Internet Gateway with name '{igw_name}' already exists.")
            igw_id = existing_igws[0]['InternetGatewayId']
        else:
            # Create the Internet Gateway
            response = client.create_internet_gateway()
            igw_id = response['InternetGateway']['InternetGatewayId']
            print("Internet Gateway created:", igw_id)

            # Add a name tag to the Internet Gateway
            client.create_tags(
                Resources=[igw_id],
                Tags=[{'Key': 'Name', 'Value': igw_name}]
            )

            # Attach the Internet Gateway to the VPC
            response = client.attach_internet_gateway(
                InternetGatewayId=igw_id,
                VpcId=vpc_id
            )
            print("Internet Gateway attached to VPC:", vpc_id)


# #Create Route table

    if vpc_id and subnet_ids:

        existing_route_tables = client.describe_route_tables(
        Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )['RouteTables']
        
        route_table_id = None

        for route_table in existing_route_tables:
            for route in route_table['Routes']:
                if route.get('GatewayId') == igw_id:
                    route_table_id = route_table['RouteTableId']
                    break


        if route_table_id:
            print("Route table already exists:", route_table_id)
        else:

            route_table_response = client.create_route_table(VpcId=vpc_id)
            route_table_id = route_table_response['RouteTable']['RouteTableId']
            print("Route table created:", route_table_id)
            
            if route_table_id:
                # Add a route to the Internet Gateway in the route table
                client.create_route(
                    RouteTableId=route_table_id,
                    DestinationCidrBlock='0.0.0.0/0',
                    GatewayId=igw_id
                )
                print("Route added to Internet Gateway in the route table.")
                
                for n in range(len(subnet_ids)):
                    # Associate the route table with the subnet
                    client.associate_route_table(
                        RouteTableId=route_table_id,
                        SubnetId=subnet_ids[n]
                    )
                    print("Route table associated with subnet:", subnet_ids[n])


# #create endpoints
    
    if subnet_ids and route_table_id:

        response = client.describe_security_groups(
            Filters=[{'Name': 'group-name', 'Values': ['default']},{'Name': 'vpc-id','Values': [vpc_id]}])
        
        sg_id = response['SecurityGroups'][0]['GroupId']
        print(f'default security is {sg_id}')

        gateway_endpoint = [
            {'ServiceName': 'com.amazonaws.us-east-1.s3'},
            {'ServiceName': 'com.amazonaws.us-east-1.dynamodb'}
        ]

        interface_endpoints = [
            {'ServiceName': 'com.amazonaws.us-east-1.ecr.dkr'},
            {'ServiceName': 'com.amazonaws.us-east-1.ecr.api'},
            {'ServiceName': 'com.amazonaws.us-east-1.sqs'},
            {'ServiceName': 'com.amazonaws.us-east-1.logs'}
        ]

        for endpoint in gateway_endpoint:

            response = client.describe_vpc_endpoints(Filters=[{'Name': 'service-name', 'Values': [endpoint['ServiceName']]}])

            if response['VpcEndpoints'][0]['ServiceName']:
               print(f"Gateway endpoint already exists: {endpoint['ServiceName']}")
            else:
                response = client.create_vpc_endpoint(
                    VpcId=vpc_id,
                    ServiceName=endpoint['ServiceName'],
                    RouteTableIds=[route_table_id] 
                )
                print(f"Gateway endpoint created: {endpoint['ServiceName']}")

        # Create or get existing interface endpoints and associate them with the appropriate subnets or route tables
        for endpoint in interface_endpoints:

            response = client.describe_vpc_endpoints(Filters=[{'Name': 'service-name', 'Values': [endpoint['ServiceName']]}])

            if response['VpcEndpoints'][0]['ServiceName']:
               print(f"Gateway endpoint already exists: {endpoint['ServiceName']}")
            else:
                response = client.create_vpc_endpoint(
                    VpcEndpointType='Interface',
                    VpcId=vpc_id,
                    ServiceName=endpoint['ServiceName'],
                    SecurityGroupIds=[sg_id],
                    SubnetIds=subnet_ids,
                    PrivateDnsEnabled=True,
                    DnsOptions={
                        'DnsRecordIpType': 'ipv4'
                    }
                )
                print(f"Interface endpoint created: {endpoint['ServiceName']}")

    return vpc_id