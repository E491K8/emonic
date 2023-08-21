import os
import base64
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.debug import DebuggedApplication
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from ..components.sessions import SessionManager
from ..components.blueprint import Blueprint
from ..core import pin_error, access_denied
from werkzeug.urls import url_encode
from itsdangerous import URLSafeTimedSerializer
import json
import mimetypes
from urllib.parse import quote as url_quote, quote_plus as url_quote_plus, urlencode as url_encode
from werkzeug.utils import send_from_directory, safe_join
import importlib
from werkzeug.local import LocalStack, LocalProxy
from datetime import datetime

class Zylo:
    def __init__(self, import_name):
        self.template_folder = 'views'
        self.url_map = Map()
        self.static_folder = "static"
        self.error_handlers = {}
        self.middlewares = []
        self.host = 'localhost'
        self.port = 8000
        self.debug = True
        self.secret_key = os.urandom(32)
        self.serializer = URLSafeTimedSerializer(base64.urlsafe_b64encode(self.secret_key))
        self.blueprints = []
        self.import_name = __name__
        self.config = {}
        self.template_backend = 'zylo.backends.ZyloTemplates'
        self.template_folder = 'views'
        self.load_settings()
        self.app_ctx_stack = LocalStack()
        self.g = LocalProxy(self._get_g)
        self.cookie_jar = {}
        self.session_manager = SessionManager(self.secret_key)
        self._app_ctx = None
        self.before_request_funcs = []
        self.after_request_funcs = []

    def load_settings(self):
        try:
            settings_module = importlib.import_module('settings')
            templates_setting = getattr(settings_module, 'TEMPLATES', None)
            self.template_backend = templates_setting[0]['BACKEND'] if templates_setting else self.template_backend
            assert self.template_backend == 'zylo.backends.ZyloTemplates', "This backend isn't supported by Zylo."
            self.template_folder = templates_setting[0]['DIRS'][0] if templates_setting and templates_setting[0]['DIRS'] else self.template_folder
            self.host = getattr(settings_module, 'HOST', self.host)
            self.port = getattr(settings_module, 'PORT', self.port)
            self.debug = getattr(settings_module, 'DEBUG', self.debug)
            self.secret_key = getattr(settings_module, 'SECRET_KEY', self.secret_key)
            self.static_folder = getattr(settings_module, 'STATIC_FOLDER', self.sta)
        except ImportError:
            pass  
        except (IndexError, KeyError, AssertionError, ValueError) as e:
            raise ValueError("Invalid TEMPLATES setting in settings.py.") from e
        self.template_env = Environment(loader=FileSystemLoader(self.template_folder))

    def add_url_rule(self, rule, endpoint, handler, methods=['GET']):
        def view_func(request, **values):
            return handler(request, **values)
        self.url_map.add(Rule(rule, endpoint=endpoint, methods=methods))
        setattr(self, endpoint, view_func)

    def route(self, rule, methods=['GET'], secure=False, pin=None, max_url_length=None, default=None, host=None, strict_slashes=None):
        def decorator(handler):
            self.add_url_rule(rule, handler.__name__, handler, methods)

            if max_url_length:
                if len(rule) > max_url_length:
                    raise ValueError(f"Rule exceeds max_url_length of {max_url_length} characters.")

            def secure_handler(request, **values): 
                if secure:
                    if request.method == 'GET':
                        response_content = access_denied(request)
                        return Response(response_content, content_type='text/html', status=403)
                    elif request.method == 'POST':
                        user_pin = request.form.get('pin')
                        if int(user_pin) != pin:
                            response_content = pin_error(request)
                            return Response(response_content, content_type='text/html', status=403)

                return handler(request, **values)

            setattr(self, handler.__name__, secure_handler)
            
            # Apply additional route options
            self.url_map.default_subdomain = default
            self.url_map.host_matching = host
            self.url_map.strict_slashes = strict_slashes
            
            return secure_handler
        return decorator

    def errorhandler(self, code):
        def decorator(handler):
            self.error_handlers[code] = handler
            return handler
        return decorator

    def use(self, middleware):
        self.middlewares.append(middleware)

    def config(self):
        return self.config
    
    def url_for_static(self, filename):
        return f'/static/{filename}'

    def serve_static(self, filename):
        static_path = os.path.join(self.static_folder, filename)
        if os.path.isfile(static_path):
            mimetype, _ = mimetypes.guess_type(static_path)
            if mimetype:
                return Response(open(static_path, 'rb').read(), mimetype=mimetype)
        raise NotFound()

    def register_blueprint(self, blueprint):
        self.blueprints.append(blueprint)

    def handle_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            handler = getattr(self, endpoint)

            # Execute before_request functions
            response = self.preprocess_request(request)
            if response:
                return response

            # Handle the actual request
            response = handler(request, **values)

            # Execute after_request functions
            response = self.postprocess_request(request, response)

        except NotFound as e:
            response = self.handle_error(404, e, request)
        except HTTPException as e:
            response = e
        return response

    def handle_error(self, code, error, request):
        handler = self.error_handlers.get(code)
        if handler:
            return handler(error, request)
        else:
            return error
        
    def before_request(self, func):
        """Decorator to register a function to be executed before each request."""
        self.before_request_funcs.append(func)
        return func

    def after_request(self, func):
        """Decorator to register a function to be executed after each request."""
        self.after_request_funcs.append(func)
        return func

    def preprocess_request(self, request):
        for func in self.before_request_funcs:
            response = func(request)
            if response:
                return response

    def postprocess_request(self, request, response):
        for func in self.after_request_funcs:
            response = func(request, response)
        return response

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        for blueprint in self.blueprints:
            if request.path.startswith(blueprint.url_prefix):
                request.blueprint = blueprint
                response = blueprint.wsgi_app(environ, start_response)
                return response

        session_id = request.cookies.get('session_id')
        session_data_str = self.session_manager.load_session(session_id)
        
        # Deserialize the session data from JSON
        if session_data_str:
            session_data = json.loads(session_data_str)
        else:
            session_data = {}

        request.session = session_data
        response = self.handle_request(request)

        # Serialize the session data to JSON before saving
        serialized_session = json.dumps(request.session)
        session_id = self.session_manager.save_session(serialized_session)

        # Set session expiration to 1 hour by default
        session_expiration = datetime.now() + self.session_manager.session_lifetime

        if isinstance(response, Response):
            response.set_cookie('session_id', session_id['session_id'], expires=session_expiration, secure=True, httponly=True)

        return response(environ, start_response)

    def __call__(self, environ, start_response):
        app = self.wsgi_app
        for middleware in reversed(self.middlewares):
            app = middleware(app)
        return app(environ, start_response)

    def run(self, host=None, port=None, debug=None, secret_key=None,
            threaded=True, processes=1, ssl_context=None, use_reloader=True, use_evalex=True):
        if host is not None:
            self.host = host
        if port is not None:
            self.port = port
        if debug is not None:
            self.debug = debug
        if secret_key is not None:
            self.secret_key = secret_key

        if self.debug:
            app = DebuggedApplication(self, evalex=use_evalex)
        else:
            app = self

        from werkzeug.serving import run_simple
        run_simple(self.host, self.port, app,
                    use_reloader=use_reloader,
                    threaded=threaded, processes=processes, ssl_context=ssl_context)
        
    def _get_g(self):
        ctx = self.app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'g'):
                ctx.g = {}
            return ctx.g
        
    def parse_date(date_string):
        return datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %Z')

    def is_resource_modified(self, request, filename, etag=None):
        file_size = os.path.getsize(filename)
        mtime = int(os.path.getmtime(filename))
        etag = etag or (file_size, mtime)
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match:
            return etag != if_none_match
        if_modified_since = request.headers.get('If-Modified-Since')
        if if_modified_since:
            if_modified_since = self.parse_date(if_modified_since)
            return datetime.utcfromtimestamp(mtime) > if_modified_since
        return True

