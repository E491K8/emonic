from werkzeug.wsgi import wrap_file
from werkzeug.http import parse_options_header
from werkzeug.datastructures import Headers
from itsdangerous import URLSafeSerializer
from werkzeug.exceptions import BadRequest
import json

class CORSMiddleware:
    def __init__(self, app, allowed_origins=None, allowed_methods=None, allowed_headers=None, expose_headers=None, allow_credentials=False, max_age=None):
        self.app = app
        self.allowed_origins = allowed_origins or []
        self.allowed_methods = allowed_methods or ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        self.allowed_headers = allowed_headers or []
        self.expose_headers = expose_headers or []
        self.allow_credentials = allow_credentials
        self.max_age = max_age

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            origin = environ.get('HTTP_ORIGIN')
            if self.is_valid_origin(origin):
                headers.append(('Access-Control-Allow-Origin', origin))
            else:
                headers.append(('Access-Control-Allow-Origin', 'null'))

            headers.append(('Access-Control-Allow-Methods', ', '.join(self.allowed_methods)))

            if self.allowed_headers:
                headers.append(('Access-Control-Allow-Headers', ', '.join(self.allowed_headers)))

            if self.expose_headers:
                headers.append(('Access-Control-Expose-Headers', ', '.join(self.expose_headers)))

            if self.allow_credentials:
                headers.append(('Access-Control-Allow-Credentials', 'true'))

            if self.max_age is not None:
                headers.append(('Access-Control-Max-Age', str(self.max_age)))

            # Apply additional security headers
            headers.append(('Strict-Transport-Security', 'max-age=31536000; includeSubDomains'))

            return start_response(status, headers, exc_info)

        try:
            response = self.app(environ, custom_start_response)
            return response
        except Exception as e:
            error_response = self.handle_error(e, environ)
            return error_response(environ, custom_start_response)

    def handle_error(self, error, environ):
        status_code = 500
        error_message = "Internal Server Error"

        if hasattr(error, 'code'):
            status_code = error.code

        if hasattr(error, 'description'):
            error_message = error.description

        response_headers = Headers()
        response_headers.add('Content-Type', 'application/json')

        error_response = {
            "error": True,
            "status_code": status_code,
            "message": error_message
        }
        return wrap_file(environ, [json.dumps(error_response)], f'{status_code} {error_message}', response_headers)

    def handle_options_request(self, environ):
        response_headers = Headers()
        response_headers.add('Content-Type', 'text/plain')
        return wrap_file(environ, ['OK'], '200 OK', response_headers)

    def is_valid_origin(self, origin):
        if '*' in self.allowed_origins:
            return True
        return origin in self.allowed_origins

    def prevent_csrf(self, environ):
        referer = environ.get('HTTP_REFERER')
        if referer and not self.is_valid_origin(referer):
            return False
        return True

    def validate_content_type(self, environ):
        content_type = environ.get('CONTENT_TYPE')
        if content_type and not any(content_type.startswith(header) for header in self.allowed_headers):
            return False
        return True

    def honeypot_mechanism(self, environ):
            user_agent = environ.get('HTTP_USER_AGENT')
            if user_agent and 'malicious' in user_agent.lower():
                return True 
            return False

def cors(app=None, origins=None, methods=None, headers=None, expose_headers=None, supports_credentials=False, max_age=None):
    if app is None:
        return CORSMiddleware(
            None,
            allowed_origins=origins,
            allowed_methods=methods,
            allowed_headers=headers,
            expose_headers=expose_headers,
            allow_credentials=supports_credentials,
            max_age=max_age
        )
    else:
        app = CORSMiddleware(
            app,
            allowed_origins=origins,
            allowed_methods=methods,
            allowed_headers=headers,
            expose_headers=expose_headers,
            allow_credentials=supports_credentials,
            max_age=max_age
        )
        return app
