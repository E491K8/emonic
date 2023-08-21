from functools import wraps
from datetime import datetime, timedelta
from werkzeug.wrappers import Response

class Limiter:
    def __init__(self, app=None):
        self.app = app
        self.default_limit = 100
        self.default_period = 60
        self.default_error_message = 'Rate limit exceeded'
        self.strategies = {}
        self.cache = {}
        self.whitelisted_ips = set()

    def limit(self, limit=None, period=None, error_message=None, strategy=None):
        def decorator(handler):
            @wraps(handler)
            def wrapped_handler(request, *args, **kwargs):
                key = self.get_key(request)
                now = datetime.now()

                limit_value = limit(request) if callable(limit) else (limit if limit is not None else self.default_limit)
                period_value = period(request) if callable(period) else (period if period is not None else self.default_period)

                if key in self.cache:
                    requests = self.cache[key]
                    valid_requests = [
                        req for req in requests if (now - req) <= timedelta(seconds=period_value)
                    ]

                    if len(valid_requests) >= limit_value:
                        message = error_message if error_message else self.default_error_message
                        return self.error_response(message, error_code='RATE_LIMIT_EXCEEDED')

                    valid_requests.append(now)
                    self.cache[key] = valid_requests
                else:
                    self.cache[key] = [now]

                return handler(request, *args, **kwargs)

            return wrapped_handler

        return decorator

    def get_key(self, request):
        return request.remote_addr

    def strategy(self, name, storage):
        def decorator(f):
            self.strategies[name] = storage
            return f
        return decorator

    def hit(self, key, amount=1):
        now = datetime.now()
        if key in self.cache:
            requests = self.cache[key]
            valid_requests = [
                req for req in requests if (now - req) <= timedelta(seconds=self.default_period)
            ]
            valid_requests.extend([now] * amount)
            self.cache[key] = valid_requests
        else:
            self.cache[key] = [now] * amount

    def reset(self, key):
        if key in self.cache:
            del self.cache[key]

    def reset_all(self):
        self.cache = {}

    def get_remaining_hits(self, key):
        if key in self.cache:
            requests = self.cache[key]
            valid_requests = [
                req for req in requests if (datetime.now() - req) <= timedelta(seconds=self.default_period)
            ]
            return self.default_limit - len(valid_requests)
        return self.default_limit

    def get_time_until_reset(self, key):
        if key in self.cache:
            requests = self.cache[key]
            latest_request_time = max(requests)
            reset_time = latest_request_time + timedelta(seconds=self.default_period)
            time_until_reset = reset_time - datetime.now()
            return max(time_until_reset, timedelta(seconds=0))
        return timedelta(seconds=0)

    def burst_limit(self, burst_limit=None, burst_period=None, error_message=None):
        def decorator(handler):
            @wraps(handler)
            def wrapped_handler(request, *args, **kwargs):
                key = self.get_key(request)
                now = datetime.now()

                burst_limit_value = (
                    burst_limit(request) if callable(burst_limit) else (burst_limit if burst_limit is not None else self.default_limit)
                )
                burst_period_value = (
                    burst_period(request) if callable(burst_period) else (burst_period if burst_period is not None else self.default_period)
                )

                if key in self.cache:
                    requests = self.cache[key]
                    valid_burst_requests = [
                        req for req in requests if (now - req) <= timedelta(seconds=burst_period_value)
                    ]

                    if len(valid_burst_requests) >= burst_limit_value:
                        message = error_message if error_message else self.default_error_message
                        return self.error_response(message, error_code='BURST_LIMIT_EXCEEDED')

                return handler(request, *args, **kwargs)

            return wrapped_handler

        return decorator

    def rate_limit_tier(self, tier_conditions, period=None, strategy=None):
        def decorator(handler):
            @wraps(handler)
            def wrapped_handler(request, *args, **kwargs):
                for limit_condition, burst_condition, tier_limit, tier_burst in tier_conditions:
                    if limit_condition(request):
                        return self.limit(limit=tier_limit, period=period, strategy=strategy)(handler)(request, *args, **kwargs)
                    if burst_condition(request):
                        return self.burst_limit(burst_limit=tier_burst, strategy=strategy)(handler)(request, *args, **kwargs)
                return handler(request, *args, **kwargs)

            return wrapped_handler

        return decorator

    def error_response(self, message, status_code=429, error_code=None):
        response = Response(message, status=status_code)
        response.headers['X-Error-Code'] = error_code
        return response

    def whitelist_ip(self, ip):
        self.whitelisted_ips.add(ip)

    def is_ip_whitelisted(self, ip):
        return ip in self.whitelisted_ips

    def ip_whitelist(self, handler):
        @wraps(handler)
        def wrapped_handler(request, *args, **kwargs):
            key = self.get_key(request)
            if self.is_ip_whitelisted(key):
                return handler(request, *args, **kwargs)
            return self.error_response('Forbidden', status_code=403, error_code='FORBIDDEN')

        return wrapped_handler
