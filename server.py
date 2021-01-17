from flask import Flask, render_template,request, redirect, url_for
from pytube import YouTube
import ssl
from os import path
from pydub import AudioSegment
import os
import io
import google.cloud.storage
from google.cloud import speech

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./creds.json"
ssl._create_default_https_context = ssl._create_stdlib_context

app = Flask(__name__)

def transcribe_gcs_with_word_time_offsets(speech_file):
    """Transcribe the given audio file asynchronously and output the word time
    offsets."""

    storage_client = google.cloud.storage.Client.from_service_account_json("creds.json")
    bucket = storage_client.get_bucket("lecture-sum")
    blob = bucket.blob(speech_file)
    blob.upload_from_filename(speech_file)
    gcs_uri = "gs://lecture-sum/lectures"

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        audio_channel_count=2,
        language_code="en-US",
        enable_word_time_offsets=True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    result = operation.result(timeout=90)
    response = {}
    response["Words"] = []
    for result in result.results:
        alternative = result.alternatives[0]
        print("Transcript: {}".format(alternative.transcript))
        response["Transcript"] = alternative.transcript
        print("Confidence: {}".format(alternative.confidence))
        response["Confidence"] = alternative.confidence

        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time

            print(
                f"Word: {word}, start_time: {start_time.total_seconds()}, end_time: {end_time.total_seconds()}"
            )
    return response;

@app.route('/download', methods=['POST'])
def post_submit():
    url = request.args.get('url')
    title = YouTube(url).streams.first().default_filename.split("/")[0].replace(' ', '_').lower().split(".")[0]
    YouTube(url).streams.first().download(filename=title)
    song = AudioSegment.from_file(title+".mp4")
    song.export(title+".flac",format = "flac")
    result = transcribe_gcs_with_word_time_offsets(title+".flac")
    return result;

if __name__ == '__main__':
	app.run(debug=True)
