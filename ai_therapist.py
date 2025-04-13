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
    """ Handle incoming Twilio call and start gathering input """
    response = VoiceResponse()
    response.say("Hello, I am your AI therapist. How are you feeling today?")

    # Use gather to collect speech input, and redirect to /process for handling
    gather = response.gather(input="speech", timeout=5, speech_timeout="auto", action="/process", method="POST")
    gather.say("Please say something, I am listening.")
    
    return str(response)

@app.route("/process", methods=["POST"])
def process_input():
    """ Process the user's speech input with AI therapist """
    user_input = request.form['SpeechResult']  # Get the speech result from the Twilio call

    # Ensure the input is available
    if user_input:
        ai_response = process_speech(user_input)  # Calls the process_speech function to get AI response
    else:
        ai_response = "I couldn't understand your input, can you please try again?"

    # Respond with AI's message
    response = VoiceResponse()
    response.say(ai_response)
    return str(response)

if __name__ == "__main__":
    # Bind to port 10000 for Render
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 if not set
    app.run(debug=True, host="0.0.0.0", port=port)
