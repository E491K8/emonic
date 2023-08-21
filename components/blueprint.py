from werkzeug.routing import Map, Rule
from werkzeug.exceptions import NotFound
from werkzeug.wrappers import Request, Response
from .sessions import session_manager
from ..components import pin_error, access_denied
import json
import os

class Blueprint:
    def __init__(self, name, import_name, url_prefix=''):
        self.name = name
        self.import_name = import_name
        self.url_prefix = url_prefix
        self.url_map = Map()
        self.error_handlers = {}
        self.before_request_funcs = []
        self.after_request_funcs = []
        self.session_manager = session_manager

    def add_url_rule(self, rule, endpoint, handler, methods=['GET']):
        rule = self.url_prefix + rule
        self.url_map.add(Rule(rule, endpoint=endpoint, methods=methods))
        setattr(self, endpoint, handler)

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

    def before_request(self, func):
        self.before_request_funcs.append(func)
        return func

    def after_request(self, func):
        self.after_request_funcs.append(func)
        return func

    def preprocess_request(self, request):
        for func in self.before_request_funcs:
            func(request)

    def postprocess_response(self, request, response):
        for func in self.after_request_funcs:
            response = func(request, response)
        return response

    def handle_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            handler = getattr(self, endpoint)
            response = handler(request, **values)
        except NotFound as e:
            response = self.handle_error(404, e)
        return response

    def handle_error(self, code, error):
        handler = self.error_handlers.get(code)
        if handler:
            return handler(error)
        else:
            response = Response(str(error), status=code)
            response.set_cookie('session_id', '', expires=0)
            return response

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        session_id = request.cookies.get('session_id')
        session_data = self.session_manager.load_session(session_id)
        
        if session_data:
            session_data = json.loads(session_data)

        request.session = session_data
        self.preprocess_request(request)
        response = self.handle_request(request)
        response = self.postprocess_response(request, response)

        serialized_session = json.dumps(request.session)
        session_id = self.session_manager.save_session(serialized_session)

        if isinstance(response, Response):
            response.set_cookie('session_id', session_id['session_id'], secure=True, httponly=True)

        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def json_response(self, data, status=200):
        return Response(json.dumps(data), status=status, content_type='application/json')

    def redirect(self, location, status=302):
        response = Response(status=status)
        response.headers['Location'] = location
        return response

    def static_file(self, filename):
        static_dir = os.path.join(os.path.dirname(self.import_name), 'static')
        file_path = os.path.join(static_dir, filename)
        
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()
            return Response(content, content_type='application/octet-stream')
        else:
            return self.handle_error(404, f'Static file "{filename}" not found')

    def add_error_handler(self, code, handler):
        self.error_handlers[code] = handler

    def add_middleware(self, middleware_func):
        self.before_request_funcs.append(middleware_func)

    def add_after_request(self, after_request_func):
        self.after_request_funcs.append(after_request_func)

    def render_template(self, template_name, **context):
        template_dir = os.path.join(os.path.dirname(self.import_name), 'templates')
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_name)
        return Response(template.render(context), content_type='text/html')

    def text_response(self, content, status=200):
        return Response(content, status=status, content_type='text/plain')

    def html_response(self, content, status=200):
        return Response(content, status=status, content_type='text/html')

    def set_cookie(self, key, value, **options):
        response = Response()
        response.set_cookie(key, value, **options)
        return response

    def clear_cookie(self, key, **options):
        response = Response()
        response.delete_cookie(key, **options)
        return response

    def json_error_response(self, message, status=400):
        error_data = {'error': message}
        return self.json_response(error_data, status)

    def xml_response(self, content, status=200):
        return Response(content, status=status, content_type='application/xml')

    def file_response(self, file_path, attachment_filename=None):
        if not os.path.isfile(file_path):
            return self.json_error_response('File not found', status=404)

        with open(file_path, 'rb') as f:
            content = f.read()

        response = Response(content, content_type='application/octet-stream')
        if attachment_filename:
            response.headers['Content-Disposition'] = f'attachment; filename="{attachment_filename}"'
        return response
