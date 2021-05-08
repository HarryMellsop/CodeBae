import boto3
import uuid
# from main import credentials

s3_resource = boto3.resource('s3', aws_access_key_id=credentials['aws_access_key_id'], aws_secret_access_key=credentials['aws_secret_access_key'])

def create_bucket_name(bucket_prefix):
    # The generated bucket name must be between 3 and 63 chars long
    return ''.join([bucket_prefix, str(uuid.uuid4())])


def create_bucket(bucket_prefix, s3_connection):
    
    session = boto3.session.Session(aws_access_key_id=credentials['aws_access_key_id'],
                                    aws_secret_access_key=credentials['aws_secret_access_key'],
                                    region_name=credentials['region-name'])
    current_region = session.region_name
    bucket_name = create_bucket_name(bucket_prefix)
    bucket_response = s3_connection.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
        'LocationConstraint': current_region})
    print(bucket_name, current_region)
    return bucket_name, bucket_response

# first_bucket_name, first_response = create_bucket(bucket_prefix='firstpythonbucket', s3_connection=s3_resource.meta.client)
print("Credentials!:")
print(credentials)
# print(first_bucket_name)
# print(first_response)