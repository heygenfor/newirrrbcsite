# encryption_utils.py
from cryptography.fernet import Fernet
from django.conf import settings

# Generate a secret key for encryption
secret_key = b'SOME_RANDOM_SECRET_KEY'

def encrypt_password(password):
    f = Fernet(secret_key)
    encrypted_password = f.encrypt(password.encode())
    return encrypted_password.decode()

def decrypt_password(encrypted_password):
    f = Fernet(secret_key)
    decrypted_password = f.decrypt(encrypted_password.encode())
    return decrypted_password.decode()
