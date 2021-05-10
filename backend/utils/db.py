from boto3.dynamodb.conditions import Key
import boto3

class UserDatabase():

    def __init__(self, 
                 credentials,
                 table_name='user-db'):

        # connect to boto3 session
        session = boto3.Session(aws_access_key_id=credentials['aws_access_key_id'],
                                aws_secret_access_key=credentials['aws_secret_access_key'],
                                region_name=credentials['region-name'])

        # get dynamo resource
        dynamo = session.resource('dynamodb')
        self.db = dynamo.Table(table_name)

    def get_user(self, user_id=None, api_key=None):
        try:
            if user_id: response = self.db.scan(FilterExpression=Key('id').eq(user_id))
            elif api_key: response = self.db.scan(FilterExpression=Key('api-key').eq(api_key))
            else: return None

            if response['ResponseMetadata']['HTTPStatusCode'] != 200: raise Exception('Bad error code.')
            elif len(response['Items']) == 0: return None
            else: return response['Items'][0]

        except Exception as e:
            print('Error fetching user: ' + str(e), flush=True)
            return None        