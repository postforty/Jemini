import os
import base64
import pytest
from app.infrastructure.security.cipher import AES256GCMCipher

def get_random_key():
    return base64.b64encode(os.urandom(32)).decode('utf-8')

def test_cipher_encryption_decryption():
    key = get_random_key()
    cipher = AES256GCMCipher(key)
    
    plaintext = "안녕하세요, Supabase 암호화 테스트입니다! 🌟"
    ciphertext = cipher.encrypt(plaintext)
    
    assert ciphertext is not None
    assert ciphertext != plaintext
    
    decrypted = cipher.decrypt(ciphertext)
    assert decrypted == plaintext

def test_cipher_invalid_key_length():
    with pytest.raises(ValueError):
        AES256GCMCipher(base64.b64encode(os.urandom(16)).decode('utf-8'))

def test_cipher_tampered_ciphertext():
    key = get_random_key()
    cipher = AES256GCMCipher(key)
    
    ciphertext = cipher.encrypt("Secret data")
    raw = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
    # Tamper with the ciphertext
    tampered_raw = raw[:-1] + (b'\x00' if raw[-1:] != b'\x00' else b'\x01')
    tampered_ciphertext = base64.urlsafe_b64encode(tampered_raw).decode('utf-8')
    
    with pytest.raises(ValueError, match="Decryption failed"):
        cipher.decrypt(tampered_ciphertext)

def test_cipher_none_handling():
    key = get_random_key()
    cipher = AES256GCMCipher(key)
    assert cipher.encrypt(None) is None
    assert cipher.decrypt(None) is None
