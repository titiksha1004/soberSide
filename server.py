from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse
from ai_therapist import process_speech
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route("/answer", methods=["GET", "POST"])
def answer_call():
    """ Handle incoming Twilio call """
    response = VoiceResponse()
    response.say("Hello, I am your AI therapist. How are you feeling today?")
    response.listen()
    return str(response)

@app.route("/process", methods=["GET", "POST"])
def process_input():
    """ Process the user's input with AI therapist """
    user_input = request.form['SpeechResult']
    ai_response = process_speech(user_input)
    
    response = VoiceResponse()
    response.say(ai_response)
    response.listen()
    return str(response)

if __name__ == "__main__":
    # Bind to port 10000 for Render
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
