# Expects files to be located in ./.aws/credentials and ./.aws/config respectively

def extract_aws_credentials():
    credentials_file = open('.aws/credentials', 'r').readlines()
    config_file = open('.aws/config', 'r').readlines()
    credentials = {}

    credentials['aws_access_key_id'] = credentials_file[1].split()[2]
    credentials['aws_secret_access_key'] = credentials_file[2].split()[2]
    credentials['region-name'] = config_file[1].split()[2]
    return credentials