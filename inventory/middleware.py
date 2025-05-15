class FilterScriptMiddleware:
    """
    Middleware to inject the filter script loader to all inventory pages.
    
    This middleware checks if the request is for an inventory page and injects
    the necessary script tag into the response to enable enhanced filtering.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if this is an HTML response
        if not hasattr(response, 'content') or not response.get('Content-Type', '').startswith('text/html'):
            return response
        
        # Check if this is an inventory page
        if '/inventory/vouchers/' not in request.path:
            return response
        
        # Inject our script tag right before </body>
        script_tag = '<script src="/static/inventory/js/filter_script_loader.js"></script>'
        
        # Convert the response content to string
        content = response.content.decode('utf-8')
        
        # Insert the script tag before the closing body tag
        if '</body>' in content:
            content = content.replace('</body>', f'{script_tag}\n</body>')
            response.content = content.encode('utf-8')
        
        return response
