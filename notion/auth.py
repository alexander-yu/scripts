import configparser
import json
import os

import click
import keyring
import requests


DEFAULT_CACHE_PATH = '.cache'
SYSTEM = 'ayu:scripts:notion'


def get_token(email=None, cache_path=DEFAULT_CACHE_PATH):
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as file:
            return json.loads(file.readlines()[0])['token_v2']

    if not email:
        config = configparser.ConfigParser()
        config.read('secrets.ini')
        email = config['client']['email']

    password = _get_password(email)

    with requests.Session() as session:
        payload = {'email': email, 'password': password}
        session.post('https://www.notion.so/api/v3/loginWithEmail', json=payload)
        cookies = session.cookies.get_dict()

    with open(cache_path, 'w') as file:
        json.dump(cookies, file)

    return cookies['token_v2']


def _get_password(email):
    password = keyring.get_password(SYSTEM, email)

    if password:
        return password

    # pylint: disable=no-value-for-parameter
    # pylint: disable=unexpected-keyword-arg
    password = _get_password_from_command_line(standalone_mode=False)
    keyring.set_password(SYSTEM, email, password)
    return password


@click.command()
@click.password_option()
def _get_password_from_command_line(password):
    return password
