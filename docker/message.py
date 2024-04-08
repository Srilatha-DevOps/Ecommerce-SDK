import boto3
import random
import os
import socket
import time
from sys import exit
import json
import string
import random
from random import randint
from fpdf import FPDF


SQS_QRL=os.environ['SQS_QRL']
S3_BUCKET=os.environ['S3_BUCKET']
DYNAMODB_TABLE=os.environ['DYNAMODB_TABLE']
#SQS_QRL="https://sqs.us-east-1.amazonaws.com/471112581276/ecommerce-queue-01"
#S3_BUCKET="ecommerce-bucket-01"
#DYNAMODB_TABLE="ecommerce-dynamodb-01"

sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')



session = boto3.session.Session()
aws_region = session.region_name
queueUrl=SQS_QRL
s3_bucket_arn = "arn:aws:s3:::{0}".format(S3_BUCKET)
print(queueUrl)
while True:
   response = sqs.receive_message(
     QueueUrl=queueUrl,
     MaxNumberOfMessages=1
   )

   print(response)
   message_in_response =  "Messages" in response

   if message_in_response == False:
      time.sleep(10)
   else:
      message = response['Messages'][0]['Body']
      receiptHandle = response['Messages'][0]['ReceiptHandle']
      message_json = json.loads(message)
      print(message_json)
      for _ in range(1):
        opId = randint(500000000, 999999999)
      name = message_json['Customer']
      email = message_json['Email']
      OrderId = message_json['OrderId']
      OrderDate = message_json['OrderDate']
      OrderAmount = message_json['OrderAmount']
      OrderStatus = message_json['OrderStatus']

      class PDF(FPDF):
         def header(self):
             # Arial bold 15
             self.set_font('Arial', 'B', 15)
             # Move to the right                                                                                                                                                                                   
             self.cell(80)
             self.cell(80, 10, 'Customer Invoice', 1, 0, 'C')
             # Line break
             self.ln(20)

      # Set font
      pdf = PDF()
      pdf.alias_nb_pages()
      pdf.add_page()
      pdf.set_font('Arial', '', 10)
      pdf.cell(0, 10, 'Name: ' + name, 0, 1, 'L')
      pdf.cell(0, 10, 'Email: ' + email, 0, 1, 'L')
      pdf.cell(0, 10, 'Order ID: ' + str(OrderId), 0, 1, 'L')
      pdf.cell(0, 10, 'Order Date: ' + OrderDate, 0, 1, 'L')
      pdf.cell(0, 10, 'Order Amount: ' + OrderAmount, 0, 1, 'L')
      pdf.cell(0, 10, 'Order Status: ' + OrderStatus, 0, 1, 'L')
      pdf.cell(0, 10, 'Thank you for you order', 0, 1, 'C')
      pdf.output(str(opId) + '.pdf', 'F')

      upload_s3 = s3.upload_file(str(opId) + '.pdf', S3_BUCKET, str(opId) + '.pdf')

      ddb_table = dynamodb.Table(DYNAMODB_TABLE)
      putItem = ddb_table.put_item(
         Item={
             'id': opId,
             'name': name,
             'email': email,
             'OrderId': OrderId,
             'OrderDate': OrderDate,
             'OrderAmount': OrderAmount,
             'OrderStatus': OrderStatus
        }
      )
      deleteMsg = sqs.delete_message(
                QueueUrl=queueUrl,
                  ReceiptHandle=receiptHandle
                  )

      os.remove(str(opId) + '.pdf')