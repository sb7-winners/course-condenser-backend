from require_login import require_login
from flask import Blueprint, Flask,request, redirect, url_for
from pytube import YouTube
import ssl
from os import path
from pydub import AudioSegment
import os
import io
import google.cloud.storage
from google.cloud import speech
import requests
import json
from firebase_admin import firestore

process_lecture = Blueprint('process_lecture', __name__)

db = firestore.client()
lectures_ref = db.collection('lectures')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./creds.json"
ssl._create_default_https_context = ssl._create_stdlib_context

def transcribe_gcs_with_word_time_offsets(speech_file):
    """Transcribe the given audio file asynchronously and output the word time
    offsets."""

    storage_client = google.cloud.storage.Client.from_service_account_json("creds.json")
    bucket = storage_client.get_bucket("lecture-sum")
    blob = bucket.blob(speech_file)
    blob.upload_from_filename(speech_file)
    gcs_uri = "gs://lecture-sum/" + speech_file

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
    full_transcript = ""
    sentences = []

    last_word = result.results[-1].alternatives[0].words[-1].word
    if "." not in last_word:
        result.results[-1].alternatives[0].words[-1].word += "."
    for result in result.results:

        alternative = result.alternatives[0]
        full_transcript += alternative.transcript
        sentence = ""

        for word_info in alternative.words:
            if sentence == "":
                start_time = ':'.join(str(word_info.start_time).split(':')[-2:])
            sentence += " "
            sentence += word_info.word

            if "." in word_info.word:
                sentences.append({
                    "start_time": start_time,
                    "sentence":sentence
                })
                sentence = ""

    response = {
        "transcript":full_transcript,
        "sentences":sentences
    }
    return response;

def summarize(transcription):
    url = "https://bert-lecture-summarizer-5e3wsetviq-uc.a.run.app/summarize_by_ratio?ratio=0.2"
    summary = requests.post(url, data = transcription["transcript"])
    transcription["summarized_transcript"] = summary.json()['summary']
    url = "https://api.smrzr.io/v1/summarize?num_sentences=7"
    key_points = requests.post(url, data = transcription["summarized_transcript"])
    transcription["key_points"] = summary.json()['summary']
    return transcription

@process_lecture.route('/processLecture', methods=['POST'])
def post_submit():
    #find url and download the video
    url = request.json["url"]
    title = YouTube(url).streams.first().default_filename.split("/")[0].replace(' ', '_').lower().split(".")[0]
    YouTube(url).streams.first().download(filename=title)
    #Format into .flac and get trranscript
    song = AudioSegment.from_file(title+".mp4")
    song.export(title+".flac",format = "flac")
    transcription = transcribe_gcs_with_word_time_offsets(title+".flac")
    #summarize
    result = summarize(transcription)
    #update firebase
    result["title"] = request.json['title']
    result["course_id"] = request.json['course_id']
    id = request.args.get('id')
    lectures_ref.document(id).set(result)
    return result;
