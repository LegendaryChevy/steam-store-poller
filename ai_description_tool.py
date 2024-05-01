import openai
import re
import os
from dotenv import load_dotenv
import json
from openai import AsyncOpenAI
from bs4 import BeautifulSoup
load_dotenv()

openai_api_key = os.getenv('OPEN_API_KEY')


openai_client = AsyncOpenAI(api_key= openai_api_key)



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
    clean_text = clean_text(text)
    
    openai_response = openai_client.chat.completions.create(

        model = "gpt-turbo-3.5",
        prompt = f"{clean_text}\n\nSummarize the description while making the game appeal to a family friendly audience for a vr cafe setting.:",
        temperature = 0.3,
        max_tokens = 60
    )

    return openai_response.choices[0].text.strip()