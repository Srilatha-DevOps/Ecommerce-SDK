import boto3
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

s3 = boto3.resource('s3')

DYNAMODB_TABLE = "ecommerce-dynamodb-01" # Replace DYNAMODB_TABLE walue if required
SENDER = "lathaasrinivas06@gmail.com"
SUBJECT = "Thank you for your order"
BODY_TEXT = ("Amazon SES Test (Python)\r\n"
             "This email was sent with Amazon SES using the "
            "AWS SDK for Python (Boto)."
            )
            
# The HTML body of the email.
BODY_HTML = """<html>
<head></head>
<body>
  <h1>Dear Customer</h1>
  <p>Thank you for purchasing the product. </p>
</body>
</html>
            """            

  
# The character encoding for the email.
CHARSET = "UTF-8"

# Create a new SES resource and specify a region.
client = boto3.client('ses')
dynamodb = boto3.client('dynamodb')

# Try to send the email.
def lambda_handler(event, context):
        s3_bucket = event['Records'][0]['s3']['bucket']['name']
        
        filename = event['Records'][0]['s3']['object']['key']
        s3.Bucket(s3_bucket).download_file(filename, '/tmp/'+filename)
        file_id = filename.split(".")[0]
        os.system("ls -la /tmp/"+filename)
        
        data = dynamodb.get_item(
            TableName=DYNAMODB_TABLE, 
             Key={
                'id': {'N': str(file_id)},
            }
            )
        email = data['Item']['email']['S']

        msg = MIMEMultipart()
        msg["Subject"] = "This is an email with an attachment!"
        msg["From"] = "lathaasrinivas06@gmail.com"
        msg["To"] = "lathaasrinivas06@gmail.com"
    
        # Set message body
        body = MIMEText("Hello, world!", "plain")
        msg.attach(body)
    
        with open("/tmp/"+filename, "rb") as attachment:
            part = MIMEApplication(attachment.read())
            part.add_header("Content-Disposition",
                            "attachment",
                            filename='invoice_'+file_id+".pdf")
        msg.attach(part)
    
        # Convert message to string and send
        ses_client = boto3.client("ses")
        response = ses_client.send_raw_email(
            Source=SENDER,
            Destinations=[email],
            RawMessage={"Data": msg.as_string()}
        )
        print(response)