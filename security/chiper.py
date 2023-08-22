import hashlib
import secrets
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import random
import string
import re
import time
from html.parser import HTMLParser

SALT_LENGTH = 16
PEPPER_LENGTH = 16

def generate_salt():
    return secrets.token_bytes(SALT_LENGTH)

def generate_pepper():
    return secrets.token_bytes(PEPPER_LENGTH)

def hash_password(password):
    salt = generate_salt()
    pepper = b'$emonic.chiper@'
    combined = salt + password.encode() + pepper

    for _ in range(20):
        combined = hashlib.sha3_512(combined).digest()
        combined = hashlib.sha3_256(combined).digest()

    iterations = 2000000
    for _ in range(iterations):
        combined = hashlib.sha3_512(combined).digest()

    final_hash = '$emonic.chiper@' + salt.hex() + combined.hex()
    return final_hash

def verify_password(password, hashed_password):
    prefix = '$emonic.chiper@'
    salt_hex = hashed_password[len(prefix): len(prefix) + 32]
    combined_hash = hashed_password[len(prefix) + 32:]
    combined = bytes.fromhex(salt_hex) + password.encode() + prefix.encode()

    for _ in range(20):
        combined = hashlib.sha3_512(combined).digest()
        combined = hashlib.sha3_256(combined).digest()

    iterations = 2000000
    for _ in range(iterations):
        combined = hashlib.sha3_512(combined).digest()

    combined_hex = combined.hex()
    generated_hash = prefix + salt_hex + combined_hex
    return generated_hash == hashed_password

def encrypt_data(password, plaintext):
    try:
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        cipher_suite = Fernet(key)

        cipher_text = cipher_suite.encrypt(plaintext.encode())
        return salt + cipher_text

    except Exception as e:
        print("Encryption error:", str(e))


def decrypt_data(password, ciphertext):
    try:
        salt = ciphertext[:16]
        cipher_text = ciphertext[16:]
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        cipher_suite = Fernet(key)

        decrypted_text = cipher_suite.decrypt(cipher_text)
        return decrypted_text.decode()

    except Exception as e:
        print("Decryption error:", str(e))


def generate_id(length=10):
    if length < 2:
        raise ValueError("Length must be at least 2.")
    starting_char = random.choice(string.ascii_lowercase)
    remaining_length = length - 2
    random_digits = ''.join(random.choice(string.digits) for _ in range(remaining_length))
    unique_id = starting_char + '-' + random_digits
    return unique_id

def validate_email(email):
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    return re.match(email_regex, email) is not None

def is_secure_password(password):
    if len(password) < 8:
        return False

    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in "!@#$%^&*()-_=+{}[]|;:,<.>/?`~" for char in password):
        return False

    return True

def chiper_key(node=None, clock_seq=None):
    from time import time
    import random

    nanoseconds = int(time() * 1e9)
    timestamp = int(nanoseconds / 100) + 0x01b21dd213814000
    clock_seq = clock_seq if clock_seq is not None else random.getrandbits(14)

    timestamp_bytes = timestamp.to_bytes(8, 'big')
    clock_seq_bytes = clock_seq.to_bytes(2, 'big')
    node = node.to_bytes(10, 'big') if node is not None else os.urandom(10)

    return b"".join([timestamp_bytes[:6], timestamp_bytes[6:], clock_seq_bytes, node])

def chiper_encode(namespace, name):
    namespace_bytes = namespace if isinstance(namespace, bytes) else namespace.encode()
    name_bytes = name.encode() if isinstance(name, str) else name

    hash_value = hashlib.md5(namespace_bytes + name_bytes).digest()
    hash_value = hash_value[:16] 

    return bytes(hash_value)

class SanitizeHTMLParser(HTMLParser):
    def __init__(self, allowed_tags=None, allowed_attributes=None):
        super().__init__()
        self.allowed_tags = allowed_tags or []
        self.allowed_attributes = allowed_attributes or []
        self.sanitized_data = []

    def handle_starttag(self, tag, attrs):
        if tag in self.allowed_tags:
            sanitized_attrs = [(attr, self.sanitize_sql_injection(value)) for attr, value in attrs if attr in self.allowed_attributes]
            sanitized_starttag = "<" + tag + " " + " ".join([attr + '="' + value + '"' for attr, value in sanitized_attrs]) + ">"
            self.sanitized_data.append(sanitized_starttag)

    def handle_endtag(self, tag):
        if tag in self.allowed_tags:
            self.sanitized_data.append("</" + tag + ">")

    def handle_data(self, data):
        self.sanitized_data.append(data)

    @staticmethod
    def sanitize_sql_injection(value):
        return re.sub(r"[\'\";]", '', value)


def sanitize_input(input_string, sanitize_html=True, sanitize_sql=True, sanitize_nosql=True):
    if sanitize_html:
        input_string = sanitize_html_input(input_string)

    if sanitize_sql:
        input_string = sanitize_sql_input(input_string)

    if sanitize_nosql:
        input_string = sanitize_nosql_input(input_string)

    return input_string


def sanitize_html_input(input_string):
    input_string = re.sub(r'<script.*?</script>', '', input_string, flags=re.DOTALL)
    input_string = re.sub(r'<style.*?</style>', '', input_string, flags=re.DOTALL)

    parser = SanitizeHTMLParser(
        allowed_tags=['p', 'br', 'strong', 'em', 'u'],
        allowed_attributes=['href', 'title']
    )
    parser.feed(input_string)

    return ''.join(parser.sanitized_data)


def sanitize_sql_input(input_string):
    return re.sub(r"[\'\";]", '', input_string)


def sanitize_nosql_input(input_string):
    return input_string.replace('$', '').replace('.', '')

class KEY:
    def __init__(self, node=None, clock_seq=None):
        self.node = node if node is not None else random.getrandbits(48)
        self.clock_seq = clock_seq if clock_seq is not None else random.getrandbits(14)
        self.variant_bits = 0b1000

    def chip1(self):
        timestamp = int(time.time() * 1e7) + 0x01b21dd213814000
        timestamp_hex = format(timestamp, '032x')
        clock_seq_hex = format(self.clock_seq, '04x')
        node_hex = format(self.node, '012x')
        uuid = f"{timestamp_hex[:8]}-{timestamp_hex[8:12]}-{timestamp_hex[12:16]}-{clock_seq_hex[0]}{timestamp_hex[16:]}-{node_hex}"
        return uuid

    def chip3(self, name, namespace_uuid):
        hash_obj = hashlib.sha1(namespace_uuid.encode('utf-8') + name.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        hash_int = int.from_bytes(hash_bytes, 'big')
        uuid = f"{hash_int:032x}"
        return uuid

    def chip4(self):
        random_bits_hex = format(random.getrandbits(128), '032x')
        uuid = f"{random_bits_hex[:8]}-{random_bits_hex[8:12]}-4{random_bits_hex[13:16]}-{self.variant_bits}{random_bits_hex[16:20]}-{random_bits_hex[20:]}"
        return uuid

    def chip2(self, domain=None):
        if domain is None:
            raise ValueError("Domain is required for version 2 UUID.")
        timestamp = int(time.time() * 1e7) + 0x01b21dd213814000
        timestamp_hex = format(timestamp, '032x')
        clock_seq_hex = format(self.clock_seq, '04x')
        node_hex = format(self.node, '012x')
        uuid = f"{domain[:8]}-{timestamp_hex[8:12]}-{timestamp_hex[12:16]}-{clock_seq_hex[0]}{timestamp_hex[16:]}-{node_hex}"
        return uuid
