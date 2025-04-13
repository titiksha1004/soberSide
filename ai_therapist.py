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

@app.route("/process", methods=["POST"])
def process_input():
    """ Process the speech input from the user """
    if request.method == 'POST':
        try:
            # Retrieve the SpeechResult from Twilio's request data
            user_input = request.form['SpeechResult']
            
            # Process the speech input using OpenAI's API
            ai_response = process_speech(user_input)

            return jsonify({"response": ai_response})  # Return AI's response as JSON
        except Exception as e:
            logging.error(f"Error processing input: {e}")
            return jsonify({"error": "Sorry, an error occurred while processing your input. Please try again."})
    
@app.route("/process", methods=["GET"])
def process_get():
    """ Optional: Handle GET requests to /process, perhaps just a simple message """
    return jsonify({"message": "Ready to process your input!"})

def process_speech(user_input):
    """ Interact with OpenAI's Chat API to process the user input """
    try:
        # Use the correct method for OpenAI's new API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use GPT-3.5 model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}  # Dynamic user input
            ]
        )

        # Extract the AI's response and return it
        ai_text = response['choices'][0]['message']['content'].strip()
        return ai_text

    except Exception as e:
        logging.error(f"Error processing speech: {e}")
        return "Sorry, an error occurred while processing your input. Please try again."

if __name__ == "__main__":
    # Bind to port 10000 for Render
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 if not set
    app.run(debug=True, host="0.0.0.0", port=port)
