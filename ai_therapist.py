from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse
import openai
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.DEBUG)

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

@app.route("/process", methods=["GET", "POST"])
def process_input():
    if request.method == 'POST':
        user_input = request.form['SpeechResult']
        ai_response = process_speech(user_input)
        return jsonify(ai_response)
    else:
        # Handle GET request, maybe just return a welcome message or status
        return jsonify({"message": "Ready to process your input!"})

def process_speech(user_input):
    try:
        # Use the correct method for v1.0.0+ of OpenAI API
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # or use another model like 'gpt-4'
            prompt=user_input,       # Use the user's input as the prompt
            max_tokens=150,          # Adjust based on your needs
            temperature=0.7,         # Control the randomness of the response
        )

        # Return the response text from OpenAI
        return response.choices[0].text.strip()

    except Exception as e:
        logging.error(f"Error processing speech: {e}")
        return "Sorry, an error occurred while processing your input. Please try again."
    
if __name__ == "__main__":
    # Bind to port 10000 for Render
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 if not set
    app.run(debug=True, host="0.0.0.0", port=port)
