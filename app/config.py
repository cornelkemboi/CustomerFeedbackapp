import os
import re

import requests
import phonenumbers
from phonenumbers import NumberParseException

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


def validate_phone_number(phone, region=None):
    try:
        # Parse the phone number
        parsed_number = phonenumbers.parse(phone, region)

        # Check if the number is valid and possible for the region
        if not phonenumbers.is_valid_number(parsed_number):
            return False, "The phone number is not valid."

        return True, phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
    except NumberParseException:
        return False, "Invalid phone number."


def is_valid_email(email):
    # Regular expression for validating an Email
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None


def is_safe_input(input_string):
    # Check for any URL patterns
    url_pattern = r'https?://[^\s]+'
    if re.search(url_pattern, input_string):
        return False

    # Check for any script or harmful tags
    malicious_pattern = r'<script>|<\/script>|<[^>]+>'
    if re.search(malicious_pattern, input_string):
        return False

    # Optionally, check for SQL injection patterns (simple check)
    sql_injection_pattern = (r'\'|"|;|--|#|\/\*|\*\/|xp_|exec|count|select|insert|update|delete|drop|create|alter'
                             r'|rename|grant|revoke')
    if re.search(sql_injection_pattern, input_string, re.IGNORECASE):
        return False

    return True
