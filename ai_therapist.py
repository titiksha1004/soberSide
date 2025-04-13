import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def process_speech(user_message):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # You can choose another model like gpt-3.5-turbo if needed
        messages=[
            {"role": "system", "content": "You are a compassionate AI therapist."},
            {"role": "user", "content": user_message}
        ]
    )
    return response['choices'][0]['message']['content']
