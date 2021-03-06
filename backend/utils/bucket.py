import boto3
import uuid
import io

class S3Bucket():

    def __init__(self,
                 credentials,
                 bucket_name='firstpythonbucket9fa1b645-bd0c-42e4-a4bb-ceddb734042a'):

        self.session = boto3.session.Session(aws_access_key_id=credentials['aws_access_key_id'],
                                    aws_secret_access_key=credentials['aws_secret_access_key'],
                                    region_name=credentials['region-name'])

        self.bucket_name = bucket_name
        self.s3_resource = boto3.resource('s3', aws_access_key_id=credentials['aws_access_key_id'], aws_secret_access_key=credentials['aws_secret_access_key'])
        self.bucket = self.s3_resource.Bucket(bucket_name)

    def save_file(self, workspace, user_data, file, file_path):
        user_ID = user_data['id']
        fileobj = io.BytesIO(file.encode()) # binarise the file for upload

        # now we save the file object with the key user_ID/workspace/file_path, which means we can easily extract
        # files relating to a user using key prefix filtering later on, and code from various workspaces
        # is kept discrete
        self.s3_resource.Object(self.bucket_name, user_ID + "/" + workspace + "/" + file_path).upload_fileobj(Fileobj=fileobj)

    def get_files(self, user_data):
        user_id = user_data['id']
        file_datas = []

        bucket = self.s3_resource.Bucket(self.bucket_name)
        for obj_sum in bucket.objects.filter(Prefix=user_id + '/'):
            obj = self.s3_resource.Object(self.bucket_name, obj_sum.key)
            file_data = obj.get()['Body'].read().decode('utf-8') 
            file_datas.append(file_data)

        return file_datas