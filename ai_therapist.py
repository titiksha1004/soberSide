from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, AI Therapist is live!"  # Simple response for root URL

@app.route("/answer", methods=["GET", "POST"])
def answer_call():
    """ Handle incoming Twilio call """
    response = VoiceResponse()
    response.say("Hello, I am your AI therapist. How are you feeling today?")

    # Use gather to collect speech input, and redirect to /process for handling
    gather = response.gather(input="speech", timeout=5, speech_timeout="auto", action="/process", method="POST")
    gather.say("Please say something, I am listening.")
    return str(response)

@app.route("/process", methods=["POST"])
def process_input():
    user_input = request.form['SpeechResult']
    ai_response = process_speech(user_input)
    
    response = VoiceResponse()
    response.say(ai_response)
    return str(response)


import openai

def process_speech(user_message):
    response = openai.Completion.create(
        model="text-davinci-003",  # Or the model you want to use
        prompt=user_message,
        max_tokens=150
    )
    return response.choices[0].text.strip()  # Fetch the response text


if __name__ == "__main__":
    # Bind to port 10000 for Render
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 if not set
    app.run(debug=True, host="0.0.0.0", port=port)
