import openai
import os
from dotenv import load_dotenv
import logging
from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.DEBUG)

# Ensure the OpenAI API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OpenAI API key not set. Please check your .env file.")

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Debug print to verify the API key loaded (remove this in production)
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

    # Use <Gather> to collect speech input and redirect to /process for handling.
    gather = response.gather(
        input="speech",
        timeout=10,
        speech_timeout="auto",
        action="/process",
        method="POST"
    )
    gather.say("Please say something, I am listening.")
    return str(response)

@app.route("/process", methods=["POST"])
def process_input():
    """ Process the speech input received from Twilio """
    if request.method == 'POST':
        # Extract speech input from the POST form data
        user_input = request.form.get('SpeechResult', '').strip()
        logging.debug(f"Received input: {user_input}")

        if not user_input:
            return jsonify({"message": "Sorry, I couldn't understand. Please try again."})
        
        ai_response = process_speech(user_input)
        return jsonify({"response": ai_response})  # Return the AI response as JSON

def process_speech(user_input):
    try:
        # Use the updated OpenAI Chat API (for version >= 1.0.0)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or "gpt-4" if you prefer
            messages=[
                {
                    "role": "system",
                    "content": "You are a compassionate therapist who listens empathetically and offers gentle advice."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            max_tokens=150
        )
        # Extract the reply from the API response
        ai_reply = response['choices'][0]['message']['content'].strip()
        logging.debug(f"AI reply: {ai_reply}")
        return ai_reply

    except Exception as e:
        logging.error(f"Error processing speech: {e}")
        return "Sorry, an error occurred while processing your input. Please try again."

if __name__ == "__main__":
    # Bind the app to port 10000 (or use the PORT environment variable if deployed)
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
