from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')

client = OpenAI(api_key=OPEN_AI_KEY)

def send_openAI_request(prompt="", optional_text=""):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f'{prompt}. {optional_text}'},
        ],
        store=True
    )

    return completion.choices[0].message.content
