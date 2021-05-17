import boto3, os
from flask import request
from botocore.client import Config

S3_KEY = os.getenv('S3_KEY')
S3_SECRET = os.getenv('S3_SECRET')
S3_BUCKET = os.getenv('S3_BUCKET')
S3_REGION = os.getenv('S3_REGION')
S3_DOMAIN = os.getenv('S3_DOMAIN')

def s3_store_images(image, filename):
    content_type = request.mimetype
    
    s3 = boto3.client('s3',
        aws_access_key_id=S3_KEY,
        aws_secret_access_key=S3_SECRET,
        region_name=S3_REGION,
    )

    file = s3.put_object(
        Body=image,
        Bucket=S3_BUCKET,
        Key=filename,
        ContentType=content_type
    )

    return file

def s3_store_file(image, filename):
    s3_store_images(image, filename)
    

def s3_get_pre_signed(file_path):
    s3 = boto3.client('s3', 
        config=boto3.session.Config(
            signature_version='s3v4'),
            region_name=S3_REGION,
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET
        )

    uri_duration = 3600 # seconds
    _uri = s3.generate_presigned_url('get_object', Params = {'Bucket': S3_BUCKET, 'Key': file_path}, ExpiresIn = uri_duration)
    return _uri


def s3_delete_file(file_path):

    session = boto3.Session(
        aws_access_key_id=S3_KEY,
        aws_secret_access_key=S3_SECRET,
        region_name=S3_REGION
    )

    s3 = session.resource("s3")
    obj = s3.Object(S3_BUCKET, file_path)
    obj.delete()

    return True

def s3_upload_file_public(file, filename):
    content_type = request.mimetype

    client = boto3.client('s3',
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET,
            aws_session_token='',
            config=Config(signature_version='s3v4')
    )
    item = client.upload_fileobj(
        file, S3_BUCKET, filename, ExtraArgs=dict(ACL='public-read'))

    return item


def s3_get_url(filepath):
    return S3_DOMAIN + filepath

