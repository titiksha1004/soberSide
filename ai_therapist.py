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

# This is the function to process the user's input with OpenAI
def process_speech(user_message):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # You can use gpt-3.5-turbo or any other model as per your requirement
        messages=[
            {"role": "system", "content": "You are a compassionate AI therapist."},
            {"role": "user", "content": user_message}
        ]
    )
    return response['choices'][0]['message']['content']

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
    user_input = request.form['SpeechResult']  # Get the speech result from the Twilio call
    ai_response = process_speech(user_input)  # This calls the process_speech function
    
    response = VoiceResponse()
    response.say(ai_response)
    response.listen()
    return str(response)

if __name__ == "__main__":
    # Bind to port 10000 for Render
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 if not set
    app.run(debug=True, host="0.0.0.0", port=port)
