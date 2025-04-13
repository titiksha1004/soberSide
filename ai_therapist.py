from flask import Flask, request, render_template
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Store call conversation history
conversation_history = {}

THERAPIST_PROMPT = """You are a compassionate, professional therapist having a phone conversation. 
Keep your responses concise and suitable for voice (2–3 sentences).
Maintain an empathetic tone while helping the caller explore their thoughts.
Always respond in a way that encourages the caller to continue sharing."""

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/answer", methods=["POST"])
def answer_call():
    resp = VoiceResponse()
    caller_id = request.values.get("From", "anonymous")

    if caller_id not in conversation_history:
        conversation_history[caller_id] = [
            {"role": "system", "content": THERAPIST_PROMPT}
        ]

    try:
        if len(conversation_history[caller_id]) == 1:
            messages = conversation_history[caller_id] + [
                {"role": "user", "content": "Begin the therapy session with a warm greeting."}
            ]
        else:
            messages = conversation_history[caller_id]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=100,
            temperature=0.7
        )

        ai_response = response.choices[0].message["content"].strip()

        if len(conversation_history[caller_id]) == 1:
            conversation_history[caller_id].append(
                {"role": "assistant", "content": ai_response}
            )

    except Exception as e:
        print(f"Error generating AI response: {e}")
        ai_response = "Hello, I'm here to listen and support you today. How are you feeling?"

    resp.say(ai_response, voice="alice")

    gather = Gather(
        input="speech",
        action="/process_speech",
        timeout=5,
        speechTimeout="auto"
    )
    gather.say("", voice="alice")
    resp.append(gather)

    resp.say("I'm here when you're ready to talk.", voice="alice")
    resp.redirect("/answer")

    return str(resp)


@app.route("/process_speech", methods=["POST"])
def process_speech():
    resp = VoiceResponse()
    caller_id = request.values.get("From", "anonymous")
    speech_result = request.values.get("SpeechResult", "")

    if not speech_result:
        resp.say("I didn't catch that. Could you please repeat?", voice="alice")
        resp.redirect("/answer")
        return str(resp)

    conversation_history[caller_id].append({"role": "user", "content": speech_result})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=conversation_history[caller_id],
            max_tokens=150,
            temperature=0.7
        )

        ai_response = response.choices[0].message["content"].strip()
        conversation_history[caller_id].append({"role": "assistant", "content": ai_response})

    except Exception as e:
        print(f"Error generating AI response: {e}")
        ai_response = "I hear you. Can you tell me more about how that makes you feel?"

    resp.say(ai_response, voice="alice")

    gather = Gather(
        input="speech",
        action="/process_speech",
        timeout=5,
        speechTimeout="auto"
    )
    gather.say("", voice="alice")
    resp.append(gather)

    resp.say("I'm still here. Please take your time.", voice="alice")
    resp.redirect("/process_speech")

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)

