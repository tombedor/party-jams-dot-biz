import boto3


def handler(event, context):
    polly = boto3.client('polly')
    s3 = boto3.client('s3')
    return {
        "url": "foo",
        "lyrics": [{"phrase": "hello", "seconds": 1.5}]
    }
