import os
import requests
from dotenv import load_dotenv

load_dotenv()


class Config:
    MYSQL_DB = os.getenv('MYSQL_DB')
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PORT = os.getenv('MYSQL_PORT')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    SECRET_KEY = os.getenv('SECRET_KEY')


def send_text_message(text, recipients, auth_token):
    base_url = "https://apis.sematime.com/v1/1536927996500/messages/single.url"
    params = {
        'text': text,
        'recipients': recipients,
        'AuthToken': auth_token
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()  # Assuming the response is in JSON format
    else:
        response.raise_for_status()
