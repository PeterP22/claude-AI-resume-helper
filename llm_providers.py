import os
from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai

load_dotenv()  # Load environment variables from .env file

class AnthropicProvider:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def analyze_resume(self, message_content):
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": message_content
                        }
                    ]
                }
            ]
        )
        return "".join([block.text for block in response.content])

class GeminiProvider:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-exp-0801",
            generation_config={
                "temperature": 0,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }
        )

    def analyze_resume(self, message_content):
        chat_session = self.model.start_chat(history=[])
        response = chat_session.send_message(message_content)
        return response.text

# You can add more provider classes here in the future