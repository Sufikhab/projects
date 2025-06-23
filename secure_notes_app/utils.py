from cryptography.fernet import Fernet
import base64
import hashlib

def get_fernet(password):
    key = hashlib.sha256(password.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))
