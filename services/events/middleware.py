from django.conf import settings
from django.http import HttpResponse

from .helpers import unpack_token

import json

class ContextTokenProcessingMiddleware():
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Middleware for unpacking the app-context token
        
        The token is retrieved from the 'app-token' url parameter.
        The unpacked user, group and app are stored in request.context as JSON
        """
        if 'app-token' in request.GET:
            #Retrieve the token
            token = request.GET.get('app-token')
            if token == None:
                return HttpResponse(status=400)
            
            #Unpack the token to the context elements
            context = unpack_token(token)
            if context == None:
                return HttpResponse(status=400)

            #Add the elements in request.context as JSON
            request.context = json.dumps(context)

