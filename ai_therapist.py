from flask import Flask, request, render_template
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os
from dotenv import load_dotenv
from twilio.twiml.voice_response import VoiceResponse


# Load environment variables
load_dotenv()

# Set up the Flask app
app = Flask(__name__)

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Route to serve the homepage
@app.route("/")
def home():
    return render_template("index.html")

# Route to handle incoming calls to Twilio
@app.route("/answer", methods=['GET', 'POST'])
def answer_call():
    response = VoiceResponse()

    # Gather user input
    gather = response.gather(input='speech', timeout=10, num_digits=1)
    gather.say("Hi, this is your AI therapist. What's on your mind?")

    # If there's no input, say "I didn't catch that"
    response.redirect('/answer')

    return str(response)

# Route to handle the speech input from the user
@app.route("/gather", methods=["POST"])
def gather_speech():
    """Process the user's speech input and get a response from OpenAI"""
    # Get the speech input from Twilio
    speech_input = request.form.get('SpeechResult')

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
    # Run the Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
