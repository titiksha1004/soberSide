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

@app.route("/process", methods=["GET", "POST"])
def process_input():
    """ Process the user's speech input with AI therapist """
    
    # Check if 'SpeechResult' exists in the request form data
    user_input = request.form.get('SpeechResult', None)  # Use get to avoid KeyError if it's missing
    
    if not user_input:
        # Log if no input is received
        return "No speech input received. Please try again.", 400
    
    # Log the user input for debugging
    print(f"User input: {user_input}")
    
    try:
        ai_response = process_speech(user_input)  # Call the process_speech function to get AI response
    except Exception as e:
        # Handle any errors that occur during the AI processing
        print(f"Error while processing speech: {str(e)}")
        ai_response = "Sorry, I encountered an error while processing your message."
    
    response = VoiceResponse()
    response.say(ai_response)
    return str(response)


if __name__ == "__main__":
    # Bind to port 10000 for Render
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 if not set
    app.run(debug=True, host="0.0.0.0", port=port)
