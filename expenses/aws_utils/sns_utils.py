import boto3
from django.conf import settings

def send_sns_alert(message, subject="Expense Alert"):
    sns = boto3.client('sns', region_name=settings.AWS_REGION)  # ✅ no credentials
    
    sns.publish(
        TopicArn=settings.AWS_SNS_TOPIC_ARN,
        Message=message,
        Subject=subject
    )
