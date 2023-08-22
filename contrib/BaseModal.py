from ..core.branch import (Emonic, 
Response, 
json,
SharedDataMiddleware,
Environment,
FileSystemLoader,
url_encode,
Map,
base64,
os,
NotFound,
HTTPException)

app = Emonic(__name__)

def render(template_name, **kwargs):
    template = app.template_env.get_template(template_name)
    kwargs['url_for_static'] = app.url_for_static
    return Response(template.render(**kwargs), mimetype='text/html')

def JsonResponse(data):
    json_data = json.dumps(data)
    return Response(json_data, mimetype='application/json')

def redirect(location, code=302):
    return Response('', status=code, headers={'Location': location})

def url_for(endpoint, **values):
        adapter = app.url_map.bind('')
        try:
            url = adapter.build(endpoint, values=values, force_external=True)
        except NotFound:
            raise ValueError(f"Endpoint '{endpoint}' not found.")
        return url

def send_file(filename, mimetype):
    with open(filename, 'rb') as f:
        content = f.read()
    headers = {'Content-Type': mimetype, 'Content-Disposition': f'attachment; filename={os.path.basename(filename)}'}
    return Response(content, headers=headers)

def static_engine(static_folder):
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {'/static': static_folder})

def template_engine(template_folder):
    app.template_env = Environment(loader=FileSystemLoader(template_folder))

def SaveJsonContent(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

def redirect_args(location, **kwargs):
    url = location
    if kwargs:
        query_params = url_encode(kwargs)
        url += f'?{query_params}'
    return Response(status=302, headers={'Location': url})

def send_from_directory(directory, filename, **options):
    return send_from_directory(directory, filename, **options)

def url_map(rules):
    return Map(rules)

def stream_with_context(generator_or_function):
    return stream_with_context(generator_or_function)

def make_unique_key():
    return base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('ascii')

def url_quote(url, safe='/', encoding=None, errors=None):
    return url_quote(url, safe=safe, encoding=encoding, errors=errors)

def url_quote_plus(url, safe='/', encoding=None, errors=None):
    return url_quote_plus(url, safe=safe, encoding=encoding, errors=errors)

def safe_join(directory, *pathnames):
    return safe_join(directory, *pathnames)

def context_processor(f):
    app.template_env.globals.update(f())

def open_resource(resource):
    return open(resource, 'rb')

def template_filter(name=None):
    def decorator(f):
        app.template_env.filters[name or f.__name__] = f
        return f
    return decorator

def url_defaults(f):
    app.url_map.url_defaults(f)

def get_template_attribute(template_name, attribute):
    return getattr(app.template_env.get_template(template_name), attribute)

def abort(code):
    raise HTTPException(code)

def make_response(response, status=200, headers=None):
    if isinstance(response, (str, bytes)):
        return Response(response, status=status, headers=headers)
    return response

def session_interface(interface):
    app.session_interface = interface

def stream_with_context(generator_or_function):
    def generate():
        for item in generator_or_function():
            yield item
    return Response(generate())

