from django.conf import settings

from Crypto.Cipher import AES

import base64
import json

def create_token(user, group, app):
    """
    Creates the token encoding the 3 context parameters using AES encryption 
    and a base64 encoding (to make the string url safe).
    Args
        user: user pk
        group: group pk
        app: app pk
    Returns
        The encoded token
    """
    #Create the padded plaintext string, length must be multiple of 16
    plain = '{}:{}:{}'.format(user, group, app)
    pad = (-len(plain) % 16) * '*'
    plain += pad
    
    #Use the django settings secret key to encrypt with AES
    key = settings.SECRET_KEY[:16]
    crypt = AES.new(key, AES.MODE_ECB)
    cipher = crypt.encrypt(plain)
    
    #Encode in base64
    token = base64.urlsafe_b64encode(cipher)
    return token

