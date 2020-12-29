import json
import os
import typing

import click
import keyring
import requests


DEFAULT_CACHE_PATH = '.cache'
EMAIL_KEY = 'Notion Email'
SYSTEM = 'ayu:scripts:notion'


def get_token(email: typing.Optional[str] = None, cache_path: str = DEFAULT_CACHE_PATH) -> str:
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as file:
            return json.loads(file.readlines()[0])['token_v2']

    if not email:
        email = _get_email()

    password = _get_password(email)

    with requests.Session() as session:
        payload = {'email': email, 'password': password}
        session.post('https://www.notion.so/api/v3/loginWithEmail', json=payload)
        cookies = session.cookies.get_dict()

    with open(cache_path, 'w') as file:
        json.dump(cookies, file)

    return cookies['token_v2']


def _get_email() -> str:
    email = keyring.get_password(SYSTEM, EMAIL_KEY)

    if email:
        return email

    email = click.prompt('Please enter your Notion email')
    keyring.set_password(SYSTEM, EMAIL_KEY, email)
    return email


def _get_password(email: str) -> str:
    password = keyring.get_password(SYSTEM, email)

    if password:
        return password

    password = click.prompt('Please enter your Notion password', hide_input=True, confirmation_prompt=True)
    keyring.set_password(SYSTEM, email, password)
    return password
