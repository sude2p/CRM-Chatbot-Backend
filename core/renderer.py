from rest_framework import renderers

import json

class UserRenderer(renderers.JSONRenderer):
    """
    Custom JSON renderer for formatting API responses.

    This renderer customizes the JSON response format. If the response data contains
    error details, it formats the response to include an 'errors' key with the error data.
    Otherwise, it returns the data as-is.

    Attributes:
        charset (str): The character set used for encoding the response. Defaults to 'utf-8'.

    Methods:
        render(data, accepted_media_type=None, renderer_context=None): 
            Converts the response data to JSON format. Formats error responses with an 'errors' key.
    """
    charset = 'utf-8'
    def render(self, data,accepted_media_type=None, renderer_context=None):
        response =''
        if 'ErrorDetail' in str(data):
            response = json.dumps({'errors':data})
        else:
            response = json.dumps(data)

        return response 

