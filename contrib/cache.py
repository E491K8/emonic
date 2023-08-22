import hashlib
import json
import time
from functools import wraps

class EmonicCache:
    def __init__(self, cache_duration=300):
        self.cache = {}
        self.cache_duration = cache_duration
    
    def _generate_key(self, func_name, args, kwargs):
        key = f"{func_name}#{args}#{kwargs}"
        return hashlib.sha256(key.encode()).hexdigest()
    
    def get(self, timeout=None, key_prefix='Emonic', unless=None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, args, kwargs)
                
                if key in self.cache:
                    cached_result, timestamp = self.cache[key]
                    if timeout is None or time.time() - timestamp <= timeout:
                        return cached_result
                
                result = func(*args, **kwargs)
                if unless is None or not unless(result):
                    self.cache[key] = (result, time.time())
                return result
            
            return wrapper
        
        return decorator
    
    def clear_cache(self):
        self.cache = {}
    
    def delete(self, func_name, *args, **kwargs):
        key = self._generate_key(func_name, args, kwargs)
        if key in self.cache:
            del self.cache[key]
    
    def memoize(self, timeout=None, key_prefix='Emonic'):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, args, kwargs)
                
                if key in self.cache:
                    cached_result, timestamp = self.cache[key]
                    if timeout is None or time.time() - timestamp <= timeout:
                        return cached_result
                
                result = func(*args, **kwargs)
                self.cache[key] = (result, time.time())
                return result
            
            return wrapper
        
        return decorator
    
    def set(self, func_name, value, *args, **kwargs):
        key = self._generate_key(func_name, args, kwargs)
        self.cache[key] = (value, time.time())
    
    def get_or_set(self, timeout=None, key_prefix='Emonic'):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, args, kwargs)
                
                if key in self.cache:
                    cached_result, timestamp = self.cache[key]
                    if timeout is None or time.time() - timestamp <= timeout:
                        return cached_result
                
                result = func(*args, **kwargs)
                self.cache[key] = (result, time.time())
                return result
            
            return wrapper
        
        return decorator
    
    def cache_for(self, cache_duration):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, args, kwargs)
                
                if key in self.cache:
                    cached_result, timestamp = self.cache[key]
                    if time.time() - timestamp <= cache_duration:
                        return cached_result
                
                result = func(*args, **kwargs)
                self.cache[key] = (result, time.time())
                return result
            
            return wrapper
        
        return decorator
    
    def cache_unless(self, condition):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, args, kwargs)
                
                if key in self.cache:
                    cached_result, timestamp = self.cache[key]
                    if not condition(cached_result):
                        return cached_result
                
                result = func(*args, **kwargs)
                if not condition(result):
                    self.cache[key] = (result, time.time())
                return result
            
            return wrapper
        
        return decorator
    
    def cache_if(self, condition):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, args, kwargs)
                
                if key in self.cache:
                    cached_result, timestamp = self.cache[key]
                    if condition(cached_result):
                        return cached_result
                
                result = func(*args, **kwargs)
                if condition(result):
                    self.cache[key] = (result, time.time())
                return result
            
            return wrapper
        
        return decorator
