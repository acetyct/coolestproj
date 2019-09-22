import logging
from transcribe_punct import transcribe_file_with_auto_punctuation
import upload
from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transc')
def transc():
    return transcribe_file_with_auto_punctuation('commercial_mono.wav')

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
