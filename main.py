import logging
from transcribe_punct import *
from upload import upload, upload_file
from pydub import AudioSegment
from flask import *
from google.cloud import storage
import wave

app = Flask(__name__)
app.secret_key = "testing"

ALLOWED_EXT = ['wav','mp3']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

@app.route('/', methods=['GET', 'POST'])
def index():
    client = storage.Client()
    bucket_name = 'lectext-253615.appspot.com'
    # bucket = client.create_bucket(bucket_name)
    bucket = client.get_bucket(bucket_name)

    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No File Found")
            return redirect(request.url)
        file = request.files['file']
        fname = file.filename

        if fname == '':
            flash("No selected file")
            return redirect(request.url)
        if file and not allowed_file(fname):
            flash("Sorry, we can't process this file format :(")
        if file and allowed_file(fname):
            mp3_to_wav(fname)
            frame_rate, channels = frame_rate_channel(fname)
            if channels > 1:
                stereo_to_mono(fname)

            blob = bucket.blob(fname)
            blob.upload_from_file(file)
            flash("File uploaded")
            return transcribe_file_with_auto_punctuation(
                f'gs://{bucket_name}/{fname}',frame_rate)
            # return transcribe_file_with_auto_punctuation(url)
    return render_template('index.html')


# @app.route('/transc')
# def transc():
#     return transcribe_file_with_auto_punctuation('commercial_mono.wav')

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml. host='127.0.0.1'
    app.run(port=8080, debug=True)
