from django.conf import settings

from Crypto.Cipher import AES

import base64

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

def unpack_token(token):
    """Inverse operation of create_token"""
    #Decode from base64
    token = base64.urlsafe_b64decode(token)

    #Decrypt AES using settings secret key
    key = settings.SECRET_KEY[:16]
    cipher = AES.new(key, AES.MODE_ECB)
    context = cipher.decrypt(token)
    
    #Seperate the elements from the string
    context = context.decode('utf-8')
    elements = context.rstrip('*').split(':')
    if len(elements) != 3:
        return None
   
    #Return the unpacked elements in a dict
    return {'user': elements[0], 'group': elements[1], 'app': elements[2]}

