import openai
import os
from dotenv import load_dotenv
import logging
from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse

# Load environment variables
load_dotenv()

# Ensure the OpenAI API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OpenAI API key not set. Please check your .env file.")

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Debug print to check if the API key is loaded correctly
print(f"Loaded OpenAI API Key: {os.getenv('OPENAI_API_KEY')}")

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
    if request.method == 'POST':
        # Access the speech result from Twilio (form data)
        user_input = request.form.get('SpeechResult', '')
        
        if not user_input:
            return jsonify({"message": "Sorry, I couldn't understand. Please try again."})
        
        ai_response = process_speech(user_input)
        return jsonify({"response": ai_response})  # Send the response as JSON

def process_speech(user_input):
    try:
        # Using the updated OpenAI API (for version >=1.0.0)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or you can use gpt-4 if you want
            messages=[{
                "role": "system", 
                "content": "You are a helpful assistant."
            }, {
                "role": "user", 
                "content": user_input  # User input as part of conversation
            }]
        )

        # Extract and return the AI's reply from the response
        ai_reply = response['choices'][0]['message']['content']  # Ensure this is correct for OpenAI v1.0.0+
        return ai_reply

    except Exception as e:
        logging.error(f"Error processing speech: {e}")
        return "Sorry, an error occurred while processing your input. Please try again."

if __name__ == "__main__":
    # Bind to port 10000 for Render or localhost
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 if not set
    app.run(debug=True, host="0.0.0.0", port=port)
