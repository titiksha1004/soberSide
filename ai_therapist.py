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
    gather = response.gather(input="speech", timeout=5, speech_timeout=5, action="/process", method="POST")
    gather.say("Please say something, I am listening.")
    return str(response)

@app.route("/process", methods=["POST"])
def process_input():
    """ Process user input after gathering from Twilio """
    if request.method == 'POST':
        # Access the speech result from Twilio (form data)
        user_input = request.form.get('SpeechResult', '')
        
        # Log the received speech input for debugging
        logging.debug(f"Received SpeechInput: {user_input}")
        
        if not user_input:
            return jsonify({"message": "Sorry, I couldn't understand. Please try again."})
        
        ai_response = process_speech(user_input)
        return jsonify({"response": ai_response})  # Send the response as JSON

def process_speech(user_input):
    try:
        # Debugging: Check the input before sending it to OpenAI
        logging.debug(f"Processing the input: {user_input}")
        
        # Using the updated OpenAI API (for version >=1.0.0)
        response = openai.completions.create(  # Updated method for the new API
            model="gpt-3.5-turbo",  # You can also use gpt-4 if you want
            prompt=user_input,  # The user input as the prompt for OpenAI
            max_tokens=150,  # Max number of tokens for the response
            n=1,  # Only generate one response
            stop=None,  # You can define stopping sequences if needed
            temperature=0.7  # Controls randomness, you can adjust this
        )

        # Extract and return the AI's reply from the response
        ai_reply = response.choices[0]['text'].strip()  # Ensure correct access to the response data
        logging.debug(f"AI Response: {ai_reply}")
        return ai_reply

    except Exception as e:
        logging.error(f"Error processing speech: {e}")
        return "Sorry, an error occurred while processing your input. Please try again."

if __name__ == "__main__":
    # Bind to port 10000 for Render or localhost
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 if not set
    app.run(debug=True, host="0.0.0.0", port=port)
