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

ns = api.namespace('stt_api_main/delete_audio', description='Google Speech API operations')


@ns.route('/delete/<string:destination_blob_name>')
class DeleteFile(Resource):
    @api.expect(pagination_arguments, validate=True)
    def delete_files(self):
        self.response.write('Deleting files...\n')
        for filename in self.tmp_filenames_to_clean_up:
            self.response.write('Deleting file %s\n' % filename)
            try:
                storage.delete(filename)
            except storage.NotFoundError:
                pass

        print('File {} deleted.'.format(filename))
        return 'File {} deleted.'.format(filename)
