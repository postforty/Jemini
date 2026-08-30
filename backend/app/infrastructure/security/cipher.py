import os
import base64
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

class AES256GCMCipher:
    """
    AES-256-GCM encryption service.
    Key must be a 32-byte (256-bit) base64 encoded string.
    """
    def __init__(self, key_b64: str):
        try:
            self.key = base64.b64decode(key_b64)
            if len(self.key) != 32:
                raise ValueError("Key must be 32 bytes (256-bit) after base64 decoding.")
            self.aesgcm = AESGCM(self.key)
        except Exception as e:
            raise ValueError(f"Invalid AES-256-GCM key provided: {e}")

    def encrypt(self, plaintext: Optional[str]) -> Optional[str]:
        if not plaintext:
            return plaintext
            
        nonce = os.urandom(12)
        plaintext_bytes = plaintext.encode('utf-8')
        
        # encrypt(nonce, data, associated_data)
        ciphertext_and_tag = self.aesgcm.encrypt(nonce, plaintext_bytes, None)
        
        # Combine nonce and ciphertext for storage
        encrypted_bytes = nonce + ciphertext_and_tag
        return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')

    def decrypt(self, ciphertext_b64: Optional[str]) -> Optional[str]:
        if not ciphertext_b64:
            return ciphertext_b64
            
        try:
            encrypted_bytes = base64.urlsafe_b64decode(ciphertext_b64.encode('utf-8'))
            
            if len(encrypted_bytes) < 28: # 12 bytes nonce + 16 bytes auth tag
                raise ValueError("Invalid ciphertext length")
                
            nonce = encrypted_bytes[:12]
            ciphertext_and_tag = encrypted_bytes[12:]
            
            plaintext_bytes = self.aesgcm.decrypt(nonce, ciphertext_and_tag, None)
            return plaintext_bytes.decode('utf-8')
            
        except InvalidTag:
            raise ValueError("Decryption failed: data was tampered with or key is incorrect.")
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
