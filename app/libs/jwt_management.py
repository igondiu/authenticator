""" Module JWT Management """

import os
import datetime
from pathlib import Path

import jwt

from app.kernels.jwt_exceptions import TokenExpiredException, DecodeException

BASE_DIR = Path(__file__).resolve().parent.parent
path_key = os.path.join(BASE_DIR, "ppkey")
path_private_key = os.path.join(path_key, "ig_auth")
path_public_key = os.path.join(path_key, "ig_auth.pub")


def verify_token_expired(token: str, token_valid_lifetime: int):
    """ Verify if a token hasn't expired yet.

    Args:
        token (str):
        token_valid_lifetime (int): The duration during which the token is considered valid.

    Returns:
        bool: False if token is not expired, True otherwise.
    """
    try:
        decoded_token = extract_payload_from_token(token)
        token_creation_time = datetime.datetime.fromtimestamp(decoded_token['iat'])
        if datetime.datetime.utcnow() - token_creation_time > datetime.timedelta(minutes=token_valid_lifetime):
            return False
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False


def generate_access_token(payload_access_token, days=0, hours=0, minutes=0, seconds=0):
    """ Generates a JWT Token.

    :param payload_access_token : Contains the data to insert into the token's payload
    :type payload_access_token: dict
    :param days: token's lifetime in days
    :type days: int
    :param hours: token's lifetime in hours
    :type hours: int
    :param minutes: token's lifetime in minutes
    :type minutes: int
    :param seconds: token's lifetime in seconds
    :type seconds: int

    :Return Type: string

    """

    if not days and not hours and not minutes and not seconds:
        raise Exception("Token lifetime can not be undefined")

    with open(path_private_key, "r") as file:
        private_key = file.read()

    expire_at = datetime.datetime.utcnow() + datetime.timedelta(days=days, hours=hours, minutes=minutes,
                                                                seconds=seconds)
    issued_at = datetime.datetime.utcnow()

    jwt_payload = {'exp': expire_at, 'iat': issued_at, 'iss': "IGondiu"}
    jwt_payload.update(payload_access_token)

    token = jwt.encode(jwt_payload, private_key, algorithm='RS256')
    if isinstance(token, bytes):
        token = token.decode('UTF-8')
    return token


def extract_payload_from_token(token):
    """ Extracts values of the given in argument attributes. """

    with open(path_public_key, "r") as file:
        public_key = file.read()
    # public_key = os.environ['PUBLIC_KEY']

    try:
        data = jwt.decode(token, public_key, algorithms='RS256')
        return data
    except jwt.exceptions.ExpiredSignatureError:
        raise TokenExpiredException("The provided token has expired")
    except Exception:
        raise DecodeException(message="Unable to decode JWT token, token is invalid")
