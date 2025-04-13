from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up the Flask app
app = Flask(__name__)

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Route to serve the homepage
@app.route("/")
def home():
    return "Welcome to the AI Therapist. This is the homepage. Calls go through /answer."

# Route to handle incoming calls to Twilio
@app.route("/answer", methods=["POST"])
def answer_call():
    """Handle incoming call from Twilio and respond with a prompt"""
    response = VoiceResponse()

    # Create a Gather verb to capture speech input from the user
    gather = Gather(input="speech", timeout=10, speechTimeout="auto", action="/process_speech", method="POST")
    gather.say("Hi, this is your AI therapist. What's on your mind?")
    response.append(gather)

    # If no speech is captured, prompt the user again
    response.say("I didn't catch that. Please call again.")
    return str(response)

# Route to handle the speech input from the user
@app.route("/process_speech", methods=["POST"])
def process_speech():
    """Process the user's speech input and get a response from OpenAI"""
    # Get the speech input from Twilio
    speech_input = request.form.get('SpeechResult')

    # If no input is received, say "I didn't catch that"
    if not speech_input:
        response = VoiceResponse()
        response.say("I didn't catch that. Can you please repeat?")
        return str(response)

    # Generate a response from OpenAI
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"You are a compassionate therapist. Respond empathetically to the following user input: {speech_input}",
        temperature=0.7,
        max_tokens=150
    )

    # Get the OpenAI response text
    ai_response = response.choices[0].text.strip()

    # Respond with the AI's response
    resp = VoiceResponse()
    resp.say(ai_response)

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
