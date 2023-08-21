from http.cookies import SimpleCookie
from ..core.branch import Zylo

app = Zylo(__name__)

class CookieManager:
    def __init__(self):
        self.cookie_jar = SimpleCookie()

    def create_cookie(self, key, value, max_age=None, expires=None, path='/', domain=None, secure=None, httponly=False, samesite=None):
        cookie = SimpleCookie()
        cookie[key] = value
        if max_age is not None:
            cookie[key]['max-age'] = max_age
        if expires is not None:
            cookie[key]['expires'] = expires
        cookie[key]['path'] = path
        if domain is not None:
            cookie[key]['domain'] = domain
        if secure:
            cookie[key]['secure'] = secure
        if httponly:
            cookie[key]['httponly'] = True
        if samesite is not None:
            cookie[key]['samesite'] = samesite
        return cookie.output(header='').strip()

    def set_cookie(self, key, value, max_age=None, expires=None, path='/', domain=None, secure=None, httponly=False, samesite=None):
        cookie = self.create_cookie(key, value, max_age, expires, path, domain, secure, httponly, samesite)
        self.cookie_jar[key] = cookie

    def get_cookie(self, key, default=None):
        return self.cookie_jar.get(key, default)

    def delete_cookie(self, key, path='/', domain=None):
        self.set_cookie(key, '', expires=0, path=path, domain=domain)
