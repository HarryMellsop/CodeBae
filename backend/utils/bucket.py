import boto3
import uuid
import io

# # eventually remove this and rely on this being a bucket class created and initialised in main
# from extract_credentials import extract_aws_credentials
# credentials = extract_aws_credentials()

# s3_resource = boto3.resource('s3', aws_access_key_id=credentials['aws_access_key_id'], aws_secret_access_key=credentials['aws_secret_access_key'])

# def create_bucket_name(bucket_prefix):
#     # The generated bucket name must be between 3 and 63 chars long
#     return ''.join([bucket_prefix, str(uuid.uuid4())])


# def create_bucket(bucket_prefix, s3_connection):
    
#     session = boto3.session.Session(aws_access_key_id=credentials['aws_access_key_id'],
#                                     aws_secret_access_key=credentials['aws_secret_access_key'],
#                                     region_name=credentials['region-name'])
#     current_region = session.region_name
#     bucket_name = create_bucket_name(bucket_prefix)
#     bucket_response = s3_connection.create_bucket(
#         Bucket=bucket_name,
#         CreateBucketConfiguration={
#         'LocationConstraint': current_region})
#     print(bucket_name, current_region)
#     return bucket_name, bucket_response

# # first_bucket_name, first_response = create_bucket(bucket_prefix='firstpythonbucket', s3_connection=s3_resource.meta.client)
# print("Credentials!:")
# print(credentials)
# # print(first_bucket_name)
# # print(first_response)

class S3Bucket():

    def __init__(self,
                 credentials,
                 bucket_name='firstpythonbucket9fa1b645-bd0c-42e4-a4bb-ceddb734042a'):

        print("Initialising S3 Bucket")
        self.session = boto3.session.Session(aws_access_key_id=credentials['aws_access_key_id'],
                                    aws_secret_access_key=credentials['aws_secret_access_key'],
                                    region_name=credentials['region-name'])

        self.bucket_name = bucket_name
        self.s3_resource = boto3.resource('s3', aws_access_key_id=credentials['aws_access_key_id'], aws_secret_access_key=credentials['aws_secret_access_key'])
        self.bucket = self.s3_resource.Bucket(bucket_name)

    def save_file(self, user_data, file, file_path):
        user_ID = user_data['id']
        fileobj = io.BytesIO(file.encode()) # binarise the file for upload

        # now we save the file object with the key user_ID + file_path, which means we can easily extract
        # files relating to a user using key prefix filtering later on
        self.s3_resource.Object(self.bucket_name, user_ID + "/" + file_path).upload_fileobj(Fileobj=fileobj)
