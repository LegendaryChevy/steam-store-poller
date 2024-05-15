import openai
import re
import os
from dotenv import load_dotenv
import json
from openai import OpenAI
from bs4 import BeautifulSoup
load_dotenv()

openai_api_key = os.getenv('OPEN_API_KEY')


openai_client = OpenAI(api_key= openai_api_key)



def clean_text(text):
    cleaned_text = re.sub(r'[^a-zA-Z0-9 /n/.]', '', text)

    text = cleaned_text

# create a new BeautifulSoup object
    soup = BeautifulSoup(text, 'lxml')

# remove all HTML tags
    text_without_html = soup.get_text()

# remove all URLs
    clean_text = re.sub(r'http\S+|www.\S+', '', text_without_html)

    return clean_text

def summarize_text_with_openai(text):
    new_text = clean_text(text)

    openai_response = openai_client.chat.completions.create(

        model = "gpt-4o",
        messages = [{
            "role": "user",
            "content":f"{new_text}\n\nSummarize the description while making the game appeal to a family friendly audience for a vr cafe setting.:"
        }
        ],
        temperature = 0.7,
        max_tokens = 500
    )

    return openai_response.choices[0].message.content.strip()
