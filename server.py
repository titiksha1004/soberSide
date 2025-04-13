from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse
from ai_therapist import process_speech
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route("/answer", methods=["GET", "POST"])
def answer_call():
    response = VoiceResponse()
    response.say("Hello, I am your AI therapist. How are you feeling today?")
    response.listen()
    return str(response)

@app.route("/process", methods=["GET", "POST"])
def process_input():
    user_input = request.form['SpeechResult']
    ai_response = process_speech(user_input)
    
    response = VoiceResponse()
    response.say(ai_response)
    response.listen()
    return str(response)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
