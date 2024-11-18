from project.middleware import ApiKeyMiddleware, JWTAuthCookieMiddleware

def api_key_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        middleware = ApiKeyMiddleware(lambda req: view_func(req, *args, **kwargs))
        return middleware(request)
    return _wrapped_view

def jwt_auth_cookie_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        middleware = JWTAuthCookieMiddleware(lambda req: view_func(req, *args, **kwargs))
        return middleware(request)
    return _wrapped_view