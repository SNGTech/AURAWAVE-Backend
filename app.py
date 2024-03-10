import glob
import json
import os
import pickle
import time
from random import randint

from flask import Flask, abort, jsonify, redirect, request, url_for
from sklearn.pipeline import Pipeline

from eeg import EEG
from predictor import ActiveLevelPredictor
from record import Recorder
from record_live import RecorderLive

app = Flask(__name__)

predictor = ActiveLevelPredictor()

# TEMPORARY STORAGE SOLUTION
music_dict = {}


def predict(input_eeg_data, input_sfreq, input_profile_info):
    eeg_dataset = EEG(input_eeg_data, input_sfreq, input_profile_info)
    prepared_data = eeg_dataset.prepare_data()

    active_level_pred = predictor.predict(prepared_data)

    music_id = randint(0, 2)

    pred = jsonify(
        {
            "active_level": active_level_pred,
            "music_name": music_dict[active_level_pred][music_id]["music_name"],
            "thumbnail_url": music_dict[active_level_pred][music_id]["thumbnail_url"],
        }
    )

    return pred


@app.route("/ping", methods=["GET"])
def ping():
    return {"command": "pong"}


# Testing only
"""@app.route("/start_session", methods=["POST"])
def start_session_test():
    if request.method == "POST":
        data = request.get_json()

        recorder = Recorder(duration=data["duration"], test_data=data)
        recorded_data = recorder.start_recording()

        return jsonify(recorded_data), 200
"""

@app.route("/record_session_live", methods=["POST"])
def record_session_live():
    if request.method == "POST":
        data = request.get_json()

        recorder = RecorderLive(duration=data["duration"])
        recorded_data = recorder.start_recording_fp1()

        return jsonify(recorded_data), 200

@app.route("/session_summary", methods=["POST"])
def session_summary():
    if request.method == "POST":
        content = request.get_json()
        pre = content["pre"]
        post = content["post"]
        
        summary = {"info": {}, "pre": {}, "post": {}}

        summary["info"]["id"] = content["id"]
        summary["info"]["timestamp"] = pre["session_start_timestamp"]
        summary["info"]['duration'] = content["duration"]
        summary["info"]['music_suggested'] = content["music_suggested"]
        summary["info"]['active_level'] = content["active_level"]

        pre_eeg = EEG(pre["eeg_data"], pre["sample_freq"], pre["profile_info"])
        summary["pre"]['eeg_summary'] = pre_eeg.get_split_freqbands_json()
        summary["pre"]['metadata'] = pre_eeg.get_metadata()

        post_eeg = EEG(post["eeg_data"], post["sample_freq"], post["profile_info"])
        summary["post"]['eeg_summary'] = post_eeg.get_split_freqbands_json()
        summary["post"]['metadata'] = post_eeg.get_metadata()

        return jsonify(summary), 200


@app.route("/predict", methods=["POST"])
def model():
    if request.method == "POST":
        # Handle no music list
        if len(music_dict) == 0:
            return abort(404)

        content = request.get_json()
        print(content)
        eeg_data = content["eeg_data"]
        sfreq = content["sample_freq"]
        profile_info = content["profile_info"]
        res = predict(eeg_data, sfreq, profile_info)

        return res, 200


@app.route("/get_music_list", methods=["GET"])
def get_music_list():
    for level in predictor.labels:
        music_dict[level] = [
            {
                "music_name": os.path.basename(x).replace(".mp3", ""),
                "thumbnail_url": os.path.basename(y),
            }
            for x, y in zip(
                glob.glob(f"./static/sample_music/{level}/*.mp3"),
                glob.glob(f"./static/sample_music/{level}/thumbnails/*.*"),
            )
        ]

    return jsonify(music_dict), 200


if __name__ == "__main__":
    app.run("localhost", 5000, debug=True)
