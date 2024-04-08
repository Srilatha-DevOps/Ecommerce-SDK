# Automated Ecommerce checkout process
This project can help you to deploy the infrastructure using AWS python SDK. Please note that the AWS SDK doesn't provide a way to store the resource statecurrent, so this project is strcuture only to create the end to end infrastrcuture. Please add the necessary modify modules according to the need.

Architecture:

![image](https://github.com/Srilatha-DevOps/Ecommerce/assets/134747767/715cd5fd-69be-43d9-8d3b-80579854e320)





Before you deploy:
* Make Sure you execute script.sh in Docker file. This will make sure to create a ECR Repo, Build the docker image and push it into the repo.
* Once the image is ready, please replace the image_uri variables in src/variables.py
* The email.zip in the src folder is include with necessary dependencies for the Email Lambda function. If want to test the end to end model, please extract the content of email.zip and replace the email id in 'email.py'. Also, verify the same email in AWS SES.

Instructions to deploy the architecture:

* Execute the main.py in src folder.

Test:
* Replace the API url and email id in the script.sh and execute it.
