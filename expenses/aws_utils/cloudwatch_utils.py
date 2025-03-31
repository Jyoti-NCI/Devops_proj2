import boto3
import datetime
from django.conf import settings

def log_to_cloudwatch(message, log_group='ExpenseTrackerLogs', stream='default'):
    logs = boto3.client('logs', region_name=settings.AWS_REGION)  # ✅ no credentials

    try:
        logs.create_log_group(logGroupName=log_group)
    except logs.exceptions.ResourceAlreadyExistsException:
        pass

    try:
        logs.create_log_stream(logGroupName=log_group, logStreamName=stream)
    except logs.exceptions.ResourceAlreadyExistsException:
        pass

    timestamp = int(datetime.datetime.now().timestamp() * 1000)

    try:
        logs.put_log_events(
            logGroupName=log_group,
            logStreamName=stream,
            logEvents=[{'timestamp': timestamp, 'message': message}]
        )
    except logs.exceptions.InvalidSequenceTokenException as e:
        pass
