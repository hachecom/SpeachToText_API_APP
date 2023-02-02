import os
from google.oauth2 import service_account
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "pg-us-n-app-629187-60485a6b99a7.json"
	projectID = "pg-us-n-app-629187"
	os.environ["GCLOUD_TESTS_PROJECT_ID"] = projectID
	os.environ["GCLOUD_TESTS_DATASET_ID"] = projectID
	os.environ["PWC_STT_API"] = "http://35.198.33.235/api"
	credentials = service_account.Credentials.from_service_account_file('pg-us-n-app-629187-60485a6b99a7.json')
	scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
	#SESSION_TYPE = 'redis'