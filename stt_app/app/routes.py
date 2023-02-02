import os
import requests
from app import app
from flask import Flask, render_template,jsonify
from flask import request, url_for, redirect, flash, session
from flask_bootstrap import Bootstrap
from flask_login import current_user, login_user, login_required, LoginManager, logout_user
from app.user import User
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm
from app import login
from werkzeug.utils import secure_filename
import threading
import time
from datetime import datetime
from gcloud import datastore

trans_list={}
ALLOWED_EXTENSIONS = set(['mp3','wav'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login.user_loader
def load_user(id):
    a = User()
    a = a.get_user(id)
    print(a)
    return a


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():

    if request.method == 'GET':
        return render_template('upload.html',title=' Upload New File')
    else:
        
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('upload',title=' Upload New File'))
        
        file = request.files['file']
        print(file)
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('upload'))
        if file and allowed_file(file.filename):
            datastore_client = datastore.Client()
            query = datastore_client.query(kind='Transcriptions')
            query.add_filter('userName', '=', current_user.username)
            query.add_filter('audioName', '=', file.filename)
            audio_list = list(query.fetch())
            if audio_list:
                flash('You already have an audio with this name')
                return redirect(url_for('upload'))
            # Create File temporary (save, read and delete it)
            temp_dir = 'app_temp_audios/'
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            name = file.filename
            file.save(temp_dir + name)
            audio_file_data = open(temp_dir + name, 'rb')
            os.remove(temp_dir + name)

            log_method('Upload',current_user.username,file.filename)

            kind = 'Transcriptions'
            key_name = file.filename + current_user.username
            task_key = datastore_client.key(kind, key_name)
            task = datastore.Entity(key=task_key, exclude_from_indexes=["description"])
            task['description'] = ''
            task['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            task['status'] = 'Processing'
            task['audioName'] = file.filename
            task['userName'] = current_user.username
            datastore_client.put(task)
            flash('Your Audio is being transcribed. To check the status, you can go to "My Transcriptions"')

            thread = threading.Thread(target=transcribe,
                                      args=[file.filename, current_user.username, audio_file_data])
            thread.start()

            return render_template('index.html')
        flash('Invalid Audio Format ( Valid ones : mp3 or wav)')
        return render_template('upload.html')


def transcribe(file_name, username, audio_file_data):
    # Transcript
    # Send file to API
    url_api = os.environ['PWC_STT_API']
    url_upload_server = url_api + "/stt_api_main/converter/upload_audio"
    file_fw = {'audio_file': audio_file_data}
    r_up = requests.post(url_upload_server, files=file_fw)
    print(r_up.status_code, r_up.reason, r_up.text)

    # Convert file
    data = r_up.json()
    audio_id = data.get('audio_id')
    file_to_convert = {'output_rate': 8000, 'audio_id': audio_id, 'output_channels_count': 1,
                       'output_format': 'wav'}
    print(file_to_convert, type(file_to_convert))
    url_convert = url_api + "/stt_api_main/converter/"
    r_con = requests.post(url_convert, json=file_to_convert)

    # Upload audio to google cloud
    data = r_con.json()
    audio_up_id = data.get('audio_id')
    audio_up_id_str = str(audio_up_id)
    bucket_name = 'sts_test_audios'
    url_upload_cloud = url_api + "/stt_api_main/audio/upload/" + bucket_name + '/' + audio_up_id_str
    r_up_cloud = requests.post(url_upload_cloud)
    data = r_up_cloud.json()
    audio_name = data.get('audio_name')
    bucket_name = data.get('bucket_name')
    json_transcriber = {
        "bucket_name": bucket_name,
        "audio_name": audio_name
    }
    url_transcriber = url_api + "/stt_api_main/stt/transcribe_from_cloud"
    r_transcribe = requests.post(url_transcriber, json=json_transcriber)

    transcription = r_transcribe.text

    # Delete audio
    url_delete = url_api + "/stt_api_main/audio/delete/" + bucket_name + '/' + audio_name
    r_delete = requests.delete(url_delete)

    datastore_client = datastore.Client()
    kind = 'Transcriptions'
    key_name = file_name+username
    task_key = datastore_client.key(kind, key_name)
    task = datastore.Entity(key=task_key, exclude_from_indexes=["description"])
    task['description'] = transcription
    task['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    task['status'] = 'Transcribed'
    task['audioName'] = file_name
    task['userName'] = username
    datastore_client.put(task)
    print('finished transcribing')
    return transcription


def log_method(activity,user,audio):
    datastore_client = datastore.Client()
    kind = 'Log'
    task_key = datastore_client.key(kind)
    task = datastore.Entity(key=task_key)
    task['userName'] = user
    task['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    task['audioName'] = audio
    task['activity'] = activity
    datastore_client.put(task)

@app.route('/dame_audio', methods=['GET'])
def dame_audio():
    global trans_list
    return jsonify(trans_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User()
        user = user.get_user(form.username.data)
        if user is None or not user.get_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title=' Log In', form=form)


@app.route('/transcriptions_list')
@login_required
def transcriptions_list():
    datastore_client = datastore.Client()
    query = datastore_client.query(kind='Transcriptions')
    query.add_filter('userName', '=', current_user.username)
    rows = list(query.fetch())
    if len(rows) == 0:
        return render_template('transcriptions_list.html',
                               title='Transcriptions List')

    return render_template('transcriptions_list.html',
                           title='Transcriptions List',
                           rows=rows)

@app.route('/log')
@login_required
def log():
    datastore_client = datastore.Client()
    query = datastore_client.query(kind='Log')
    query.order = ['timestamp']
    rows = list(query.fetch())
    if not current_user.admin:
        rows_aux = []
        for row in rows:
            if row['userName'] == current_user.username:
                rows_aux.append(row)
        rows = rows_aux

    return render_template('log.html',
                           title='Overview',
                           rows=rows, admin=current_user.admin)


@app.route('/transcription_main', methods=['GET', 'POST'])
@login_required
def transcription_main():

    audioname=request.form.get('audio')
    datastore_client = datastore.Client()
    query = datastore_client.query(kind='Transcriptions')
    query.add_filter('userName', '=', current_user.username)
    query.add_filter('audioName', '=', audioname)
    rows = list(query.fetch())
    return render_template('transcription_main.html',transcription=audioname,description=rows[0]['description'])

@app.route('/save_changes', methods=['POST'])
@login_required
def save_changes():
    text=request.form.get('text')
    audio_name=request.form.get('audio')
    #audio_name='test_audio_parteMil.mp3'
    log_method('Edit',current_user.username,audio_name)
    datastore_client = datastore.Client()
    kind = 'Transcriptions'
    name = audio_name + current_user.username
    task_key = datastore_client.key(kind, name)
    task = datastore.Entity(key=task_key, exclude_from_indexes=["description"])
    task['description'] = text
    task['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    task['status'] = 'Transcribed'
    task['audioName'] = audio_name
    task['userName'] = current_user.username
    datastore_client.put(task)
    flash('Your transcription has been successfully edited')
    return redirect(url_for('transcriptions_list'))




@app.route('/delete_transcription', methods=['POST'])
@login_required
def delete_transcription():
    audio_delete = request.form.get('delete')
    audio_user = audio_delete+current_user.username
    datastore_client = datastore.Client()
    key = datastore_client.key('Transcriptions', audio_user)
    task = datastore_client.get(key)
    datastore_client.delete(task.key)

    log_method('Delete', current_user.username, audio_delete)

    flash('Audio: {} deleted successfully'.format(audio_delete))
    return redirect(url_for('transcriptions_list'))

if __name__ == '__main__':
    app.run(debug=True)
