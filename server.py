from flask import Flask, render_template,request, redirect, url_for
from pytube import YouTube
import ssl
from os import path
from pydub import AudioSegment
import os
import io
import google.cloud.storage
from google.cloud import speech
import requests

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
        enable_automatic_punctuation=True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    result = operation.result(timeout=90)
    results = []
    full_transcript = ""
    for result in result.results:
        alternative = result.alternatives[0]
        full_transcript += alternative.transcript
        transcription = {
            "Transcript":alternative.transcript,
            "Confidence":alternative.confidence,
            "Items":[]
        }
        for word_info in alternative.words:
            transcription["Items"].append({
                "word":word_info.word,
                "start_time":':'.join(str(word_info.start_time).split(':')[:2]),
                "end_time":':'.join(str(word_info.end_time).split(':')[:2])
            })
        results.append(transcription)
    response = {
        "transcript":full_transcript,
        "results":results
    }
    return response;

def summarize(transcription):
    url = "https://bert-lecture-summarizer-5e3wsetviq-uc.a.run.app/summarize_by_ratio?ratio=0.2"
    summary = requests.post(url, data = transcription["transcript"])
    transcription["summarized_transcript"] = summary
    keyPoints = requests.post(url, data = transcription["transcript"])
    transcription["key_points"] = keyPoints
    return transcription

@app.route('/processLecture', methods=['POST'])
def post_submit():
    url = request.args.get('url')
    title = YouTube(url).streams.first().default_filename.split("/")[0].replace(' ', '_').lower().split(".")[0]
    YouTube(url).streams.first().download(filename=title)
    song = AudioSegment.from_file(title+".mp4")
    song.export(title+".flac",format = "flac")
    transcription = transcribe_gcs_with_word_time_offsets(title+".flac")
    result = summarize(transcription)
    return result;

if __name__ == '__main__':
	app.run(debug=True)
