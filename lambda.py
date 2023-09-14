import boto3
import os
import sys
import uuid
from urllib.parse import unquote_plus



s3_client = boto3.client('s3')


def emailsubscription(sns_resource, topic_arn, email):
    response = sns_resource.list_subscriptions_by_topic(TopicArn=topic_arn)
    for subscription in response['Subscriptions']:
        if subscription['Protocol'] == 'email' and subscription['Endpoint'] == email:
            return True
    return False

def message(original_path,key):
   print(original_path)
   filename=os.path.basename(original_path)
   print("Original File Name:", filename)
   #Reading the file
   with open(original_path, 'r') as txt_file:
      lines = txt_file.readlines()
      emails = lines[0].split(': ')[1].strip().split(', ')
      file_url = lines[1].split(': ')[1].strip()
      description = lines[2].split(': ')[1].strip()

   subject = 'Image Upload Notification'
   topic_arn = ""  
    #provide the access key and secret key
   sns_resource= boto3.client("sns",
      aws_access_key_id= '##Access_key' ,
      aws_secret_access_key= '##Secret_key',
      region_name = 'us-east-1')
   
   
   topicname="peragana_topic"
   topics = sns_resource.list_topics()

   for topic in topics['Topics']:
      if topicname in topic['TopicArn']:
         topic_arn=topic['TopicArn']

   if(topic_arn==""):
          topic_arn = sns_resource.create_topic(Name=topicname)['TopicArn']

   print("topic arn ",topic_arn)

   for email in emails:

       
      is_subscribed = emailsubscription(sns_resource, topic_arn, email)

      if not is_subscribed:
         #send subscription mail 
         message1 = f"Dear user,\n\nYou have been subscribed to receive notifications."
         sns_resource.publish(TopicArn=topic_arn, Message=message1, Subject=subject, MessageAttributes={'email': {'DataType': 'String', 'StringValue': email}})
         print(f"Subscription notification sent to {email}")
         # Subscribe the email to the topic
         sns_resource.subscribe(TopicArn=topic_arn, Protocol='email', Endpoint=email)


      #if subscribed
      message = f"Dear user,\n\nAn image with filename {key} has been uploaded.\n\nFile URL: {file_url}\n\nDescription: {description}"
      sns_resource.publish(TopicArn=topic_arn, Message=message, Subject=subject, MessageAttributes={'email': {'DataType': 'String', 'StringValue': email}})
      print(f"Notification sent to {email}")
        

 
def lambda_handler(event, context):
   print('Send email notifications using sns')
   for record in event['Records']:
      bucket = record['s3']['bucket']['name']
      key = unquote_plus(record['s3']['object']['key'])
      print("Bucker =",bucket)
      print("key =",key)
      tmpkey = key.replace('/', '')
      download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
      s3_client.download_file(bucket, key, download_path)
      message(download_path,key)
   print('ALL Notifications Sent')
