"""
Custom renderers for the API.
"""
from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    """
    Custom JSON renderer that wraps responses in a consistent format.
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render data into JSON, wrapping in standard response format.
        """
        # If the response is already wrapped, don't double-wrap
        if isinstance(data, dict) and 'status' in data:
            return super().render(data, accepted_media_type, renderer_context)
        
        # Wrap successful responses
        response_data = {
            'status': 'success',
            'data': data,
        }
        
        return super().render(response_data, accepted_media_type, renderer_context)

