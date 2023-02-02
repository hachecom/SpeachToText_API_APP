from flask_restplus import Resource
from flask_restplus import reqparse
from google.cloud import speech
from google.cloud import storage

from stt_api_main.api.restplus import api

pagination_arguments = reqparse.RequestParser()
pagination_arguments.add_argument('bucket name', type=str, required=True, default=1, help='enter bucket name')

client = speech.SpeechClient()

# GOOGLE IMPORTS
# from

ns = api.namespace('stt_api_main/list_audio', description='Google Speech API operations')


@ns.route('/list_objects/<string:bucket_name>')
class ListObjects(Resource):

    def get(self, bucket_name):
        """Lists all the blobs in the bucket."""
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)

        blobs = bucket.list_blobs()

        for blob in blobs:
            print(blob.name)

        # return json.blobs

