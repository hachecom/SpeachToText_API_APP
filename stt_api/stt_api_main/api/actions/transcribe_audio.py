from flask_restplus import Resource
from flask_restplus import reqparse
from google.cloud import speech
from google.cloud.speech import types

from stt_api_main.api.restplus import api

pagination_arguments = reqparse.RequestParser()
pagination_arguments.add_argument('bucket name', type=str, required=True, default=1, help='enter bucket name')

client = speech.SpeechClient()

# GOOGLE IMPORTS
# from

ns = api.namespace('stt_api_main/transcribe_audio', description='Google Speech API operations')


@ns.route('/transcription/<string:gcs_audio_uri>')
class Transcription(Resource):

    def get(self, gcs_audio_uri):
        """Returns transcribed text for an audio file uploaded to
        Google Cloud Storage from it's URI"""
        gcs_uri = 'gs://sts_test_audios/' + gcs_audio_uri + '.wav'
        print(gcs_uri)
        audio = types.RecognitionAudio(uri=gcs_uri)
        config = types.RecognitionConfig(
            # encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
            # sample_rate_hertz=16000,
            language_code='en-US')

        operation = client.long_running_recognize(config, audio)

        print('Waiting for operation to complete...')
        response = operation.result()
        print(response)

        # Each result is for a consecutive portion of the audio. Iterate through
        # them to get the transcripts for the entire audio file.
        # for result in response.results:
        #    # The first alternative is the most likely one for this portion.
        #    print(u'Transcript: {}'.format(result.alternatives[0].transcript))
        #    print('Confidence: {}'.format(result.alternatives[0].confidence))
        return response.results[0].alternatives[-1].transcript
    # return "aca va la transcription de "+gcp_audio_uri