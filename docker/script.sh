#Create Repo
py main.py

#Create and Push Docker image

docker build -t ecommerce-image .

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker push <account>.dkr.ecr.us-east-1.amazonaws.com/ecommerce-repo:latest