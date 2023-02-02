import subprocess
from flask_restplus import Resource
from stt_api_main.api.restplus import api

ns = api.namespace('stt_api_main/convert_audio', description='Google Speech API operations')


@ns.route('/convert/<string:destination_blob_name>')
class ConvertFile(Resource):
    command = "ffmpeg -i /media/sf_DownloadsWin/financial-wellness-callcenter_5405CA83002C1650-1.wma -ac 1 -ar 8000 " \
              "-vn /home/anto/google-cloud-speech/financial-wellness-callcenter_5405CA83002C1650-1_8k.wav "
    subprocess.call(command, shell=True)
