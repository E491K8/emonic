import os
import base64
from cryptography.fernet import Fernet
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
import hashlib
import hmac

class SessionManager:
    def __init__(self, secret_key, session_lifetime=3600, cookie_name='session_id', cookie_path='/', secure=False, http_only=True):
        self.secret_key = secret_key
        self.serializer = URLSafeTimedSerializer(secret_key)
        self.cipher_suite = Fernet(base64.urlsafe_b64encode(secret_key))
        self.session_lifetime = timedelta(seconds=session_lifetime)
        self.cookie_name = cookie_name
        self.cookie_path = cookie_path
        self.secure = secure
        self.http_only = http_only
        self.session_data = {}

    def encode_data(self, data):
        serialized_data = self.serializer.dumps(data)
        encrypted_data = self.cipher_suite.encrypt(serialized_data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')

    def decode_data(self, data):
        encrypted_data = base64.urlsafe_b64decode(data.encode('utf-8'))
        decrypted_data = self.cipher_suite.decrypt(encrypted_data).decode('utf-8')
        return self.serializer.loads(decrypted_data)

    def generate_expiration(self):
        return datetime.now() + self.session_lifetime

    def save_session(self, session_data, **kwargs):
        session_id = self.encode_data(session_data)
        expiration = self.generate_expiration()
        return {'session_id': session_id, 'expiration': expiration, **kwargs}

    def load_session(self, session_id):
        try:
            session_data = self.decode_data(session_id)
        except Exception:
            session_data = {}
        return session_data

    def is_session_expired(self, expiration):
        return datetime.now() > expiration

    def validate_session(self, session_id):
        session_data = self.load_session(session_id)
        if not session_data:
            return False, {}
        
        expiration = session_data.get('expiration')
        if expiration and not self.is_session_expired(expiration):
            return True, session_data
        else:
            return False, {}

    def get_cookie_name(self):
        return self.cookie_name

    def get_cookie_options(self):
        options = {
            'path': self.cookie_path,
            'secure': self.secure,
            'httponly': self.http_only,
        }
        return options

    def generate_signature(self, data):
        signature = hmac.new(self.secret_key, data.encode('utf-8'), hashlib.sha256)
        return signature.hexdigest()

    def validate_signature(self, data, signature):
        expected_signature = self.generate_signature(data)
        return hmac.compare_digest(expected_signature, signature)
    
    def set_session_lifetime(self, session_lifetime):
        self.session_lifetime = timedelta(seconds=session_lifetime)

    def renew_session(self, session_id):
        # Extend the expiration time of an existing session
        session_data = self.load_session(session_id)
        if session_data:
            expiration = self.generate_expiration()
            return self.save_session(session_data, expiration=expiration)

    def touch(self, session_id):
        # Update the expiration time of an existing session without modifying its content
        session_data = self.load_session(session_id)
        if session_data:
            return self.save_session(session_data)

    def pop(self, key, default=None):
        # Remove a key from the session and return its value
        return self.session_data.pop(key, default)

    def clear(self):
        # Clear all data from the session
        self.session_data.clear()

    def set(self, key, value):
        # Set a value in the session
        self.session_data[key] = value

    def get(self, key, default=None):
        # Get a value from the session
        return self.session_data.get(key, default)

    def update(self, data):
        # Update session data with a dictionary
        self.session_data.update(data)

# Create a global instance of the session manager
secret_key = os.urandom(32)
session_manager = SessionManager(secret_key)
