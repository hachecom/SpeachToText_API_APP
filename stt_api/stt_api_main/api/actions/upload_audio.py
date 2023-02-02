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

ns = api.namespace('stt_api_main/upload_audio', description='Google Speech API operations')


@ns.route('/upload/<string:destination_blob_name>')
class UploadFile(Resource):
    @api.expect(pagination_arguments, validate=True)
    def post(self, destination_blob_name, bucket_name):
        """Delete a file from the bucket"""
        # bucket_name = "sts_test_audios"
        source_file_name = "/home/anto/google-cloud-speech/audio_test.wav"

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        print('File {} uploaded to {}.'.format(source_file_name, destination_blob_name))
        return 'File {} uploaded to {}.'.format(source_file_name, destination_blob_name)
