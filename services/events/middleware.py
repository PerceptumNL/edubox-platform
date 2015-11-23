from django.conf import settings
from django.http import HttpResponse

from Crypto.Cipher import AES

import base64
import json

class ContextTokenProcessingMiddleware():
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Middleware for unpacking the app-context token
        
        The token is retrieved from the 'app-token' url parameter.
        The unpacked user, group and app are stored in request.context as JSON
        """
        #Only unpack for POST methods to the LRS
        if request.method == 'POST' and request.resolver_match.url_name == 'api':
            #Retrieve the token
            token = request.GET.get('app-token')
            if token == None:
                return HttpResponse(status=400)
            
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
                return HttpResponse(status=400)
            
            #Add the elements in request.context as JSON
            user, group, app = elements
            request.context = json.dumps({'user': user, 'group': group, 'app': app})

