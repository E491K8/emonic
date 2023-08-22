from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound, MethodNotAllowed, BadRequest
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.middleware.profiler import ProfilerMiddleware
import json
from xml.etree import ElementTree as ET

class EmonicRestful:
    def __init__(self):
        self.url_map = Map()
        self.resources = {}
        self.middlewares = []
        self.error_handlers = {}
        self.debug = False

    def route(self, rule, **options):
        def decorator(func):
            endpoint = func.__name__
            rule_obj = Rule(rule, endpoint=endpoint, **options)
            self.url_map.add(rule_obj)
            self.resources[endpoint] = func
            return func
        return decorator

    def get(self, rule, **options):
        return self.route(rule, methods=['GET'], **options)

    def post(self, rule, **options):
        return self.route(rule, methods=['POST'], **options)

    def put(self, rule, **options):
        return self.route(rule, methods=['PUT'], **options)

    def delete(self, rule, **options):
        return self.route(rule, methods=['DELETE'], **options)

    def add_resource(self, resource_class, route, **kwargs):
        resource = resource_class(self, **kwargs)
        endpoint = resource.__class__.__name__.lower()
        rule_obj = Rule(route, endpoint=endpoint)
        self.url_map.add(rule_obj)
        self.resources[endpoint] = resource

    def errorhandler(self, code):
        def decorator(func):
            self.add_error_handler(code, func)
            return func
        return decorator

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            resource = self.resources.get(endpoint)
            if resource:
                if request.method == 'OPTIONS':
                    return self.handle_options(resource)
                response_data = resource.dispatch_request(request, **values)
                response = self.make_response(response_data, request)
                return response
            else:
                return self.handle_error(404, "Not Found", request)
        except HTTPException as e:
            return self.handle_error(e.code, e.description, request)

    def handle_options(self, resource):
        allowed_methods = resource.get_allowed_methods()
        headers = {'Allow': ', '.join(allowed_methods)}
        return Response(status=200, headers=headers)

    def handle_error(self, code, message, request):
        if code in self.error_handlers:
            handler = self.error_handlers[code]
            response_data = handler(code, message, request)
        else:
            response_data = {'error': message}
        return self.make_response(response_data, request, status=code)

    def add_error_handler(self, code, handler_func):
        self.error_handlers[code] = handler_func

    def make_response(self, response_data, request, status=200, headers=None):
        if not headers:
            headers = {}

        content_type = self.negotiate_content_type(request)
        response = None

        if content_type == 'application/json':
            response = self.make_json_response(response_data, status, headers)
        elif content_type == 'application/xml':
            response = self.make_xml_response(response_data, status, headers)

        response.cache_control.no_cache = True  # Disable browser caching by default
        return response


    def make_json_response(self, response_data, status=None, headers=None):
        if status is None:
            status = 200
        if headers is None:
            headers = {}

        response = Response(json.dumps(response_data), status=status, headers=headers)
        response.content_type = 'application/json'
        return response

    def make_xml_response(self, response_data, status=None, headers=None):
        if status is None:
            status = 200
        if headers is None:
            headers = {}

        root = ET.Element('response')
        self.build_xml_element(root, response_data)

        xml_str = ET.tostring(root, encoding='utf-8', method='xml')
        response = Response(xml_str, status=status, headers=headers)
        response.content_type = 'application/xml'
        return response

    def build_xml_element(self, parent, data):
        if isinstance(data, dict):
            for key, value in data.items():
                element = ET.SubElement(parent, key)
                self.build_xml_element(element, value)
        elif isinstance(data, list):
            for item in data:
                element = ET.SubElement(parent, 'item')
                self.build_xml_element(element, item)
        else:
            parent.text = str(data)

    def negotiate_content_type(self, request):
        accepted_types = request.headers.get('Accept', '').split(',')
        for accepted_type in accepted_types:
            if 'application/json' in accepted_type:
                return 'application/json'
            elif 'application/xml' in accepted_type:
                return 'application/xml'
        return 'application/json'
    
    def handle_exception(self, e, request):
        response_data = {'error': str(e)}
        return self.make_response(response_data, request, status=getattr(e, 'code', 500))

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        try:
            response = self.dispatch_request(request)
        except HTTPException as e:
            response = self.handle_exception(e, request)
        return response(environ, start_response)

    def run(self, host='localhost', port=3000, debug=False):
        self.debug = debug
        if debug:
            app = DispatcherMiddleware(self.wsgi_app, {'/__debug__': ProfilerMiddleware(self.wsgi_app)})
            from werkzeug.debug import DebuggedApplication
            app = DebuggedApplication(app, evalex=True)
        else:
            app = self.wsgi_app
        from werkzeug.serving import run_simple
        run_simple(host, port, app, use_reloader=debug)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

class Resource:
    def __init__(self, app):
        self.app = app

    def dispatch_request(self, request, **kwargs):
        method = request.method.lower()
        handler = getattr(self, method, None)
        if handler:
            return handler(request, **kwargs)
        raise MethodNotAllowed(valid_methods=self.get_allowed_methods())
    
    def validate_input(self, request, required_fields):
        json_data = request.get_json()
        if json_data is None:
            raise BadRequest("Invalid JSON input")

        missing_fields = [field for field in required_fields if field not in json_data]
        if missing_fields:
            raise BadRequest(f"Missing required fields: {', '.join(missing_fields)}")

        return json_data

    def get_allowed_methods(self):
        allowed_methods = []
        for method in dir(self):
            if method.upper() in ['GET', 'POST', 'PUT', 'DELETE']:
                allowed_methods.append(method.upper())
        return allowed_methods

class Api:
    def __init__(self, app):
        self.app = app
        self.endpoints = []

    def add_resource(self, resource_class, route, **kwargs):
        resource = resource_class(self.app, **kwargs)
        self.app.add_resource(resource_class, route, **kwargs)
        self.endpoints.append((resource_class, route))

    def marshal(self, data, fields):
        return {field: data[field] for field in fields}

    def parse_json(self, request, required_fields=None):
        json_data = request.get_json()
        if required_fields and json_data is None:
            raise BadRequest("Invalid JSON input")

        if required_fields:
            missing_fields = [field for field in required_fields if field not in json_data]
            if missing_fields:
                raise BadRequest(f"Missing required fields: {', '.join(missing_fields)}")

            return {field: json_data[field] for field in required_fields}
        
        return json_data

    def output(self, data, code, headers=None):
        response = self.app.make_response(data, status=code, headers=headers)
        return response

class Pagination:
    def __init__(self, items, page, per_page):
        self.items = items
        self.page = page
        self.per_page = per_page

    def paginate(self):
        total = len(self.items)
        pages = total // self.per_page
        if total % self.per_page != 0:
            pages += 1

        start_idx = (self.page - 1) * self.per_page
        end_idx = start_idx + self.per_page
        paginated_items = self.items[start_idx:end_idx]

        pagination_info = {
            'page': self.page,
            'per_page': self.per_page,
            'total_pages': pages,
            'total_items': total
        }

        return paginated_items, pagination_info

class RequestParser:
    def __init__(self, request):
        self.request = request

    def parse_args(self, **expected_args):
        args = {}
        for arg_name, arg_type in expected_args.items():
            if arg_name in self.request.args:
                args[arg_name] = arg_type(self.request.args[arg_name])
        return args

    def parse_json(self, required_fields=None):
        json_data = self.request.get_json()
        if required_fields and json_data is None:
            return None
        if required_fields:
            return {field: json_data[field] for field in required_fields}
        return json_data
    
class ErrorHandlers:
    @staticmethod
    def handle_400(code, message, request):
        return {'error': message}, code

    @staticmethod
    def handle_404(code, message, request):
        return {'error': message}, code

    @staticmethod
    def handle_405(code, message, request):
        return {'error': message}, code

    @staticmethod
    def handle_500(code, message, request):
        return {'error': message}, code

    @staticmethod
    def handle_503(code, message, request):
        return {'error': message}, code
