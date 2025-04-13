from flask import Flask, request, render_template
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/answer", methods=["POST"])
def answer_call():
    response = VoiceResponse()
    gather = Gather(input="speech", timeout=5, action="/process", method="POST")
    gather.say("Hi, this is your AI therapist. What's on your mind?")
    response.append(gather)
    response.say("I didn't catch that. Please call again.")
    return str(response)

@app.route("/process", methods=["POST"])
def process_speech():
    user_input = request.form.get("SpeechResult")
    if not user_input:
        return "<Response><Say>I didn't hear anything. Goodbye.</Say></Response>"

    system_prompt = (
        "You are a compassionate therapist specializing in substance abuse. "
        "Respond with empathy and brief, supportive advice. Keep it under 3 sentences."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=100,
        temperature=0.7,
    )

    reply = completion.choices[0].message.content.strip()

    response = VoiceResponse()
    response.say(reply)
    return str(response)

# Required for Render to expose the app properly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
