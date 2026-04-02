import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

IV_LENGTH = 16
ITERATION_COUNT = 65536
KEY_LENGTH = 32  # 256 bits = 32 bytes (Java uses 256 bit key length)


class NebulaEncryption:
    def __init__(self, secret_key: str, salt: str):
        self.secret_key = secret_key
        self.salt = salt

    def _derive_key(self) -> bytes:
        """Derive key using PBKDF2-HMAC-SHA256 to match Java's PBKDF2WithHmacSHA256"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=KEY_LENGTH,
            salt=self.salt.encode("utf-8"),
            iterations=ITERATION_COUNT,
            backend=default_backend()
        )
        return kdf.derive(self.secret_key.encode("utf-8"))


    def encrypt(self, value: str) -> str:
        iv = os.urandom(IV_LENGTH)
        key = self._derive_key()

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(value.encode("utf-8")) + padder.finalize()

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        cipher_text = encryptor.update(padded_data) + encryptor.finalize()

        cipher_with_iv = iv + cipher_text
        return base64.b64encode(cipher_with_iv).decode("utf-8")


    def decrypt(self, value: str) -> str:
        cipher_with_iv = base64.b64decode(value)
        iv = cipher_with_iv[:IV_LENGTH]
        cipher_text = cipher_with_iv[IV_LENGTH:]

        key = self._derive_key()

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plain = decryptor.update(cipher_text) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        original = unpadder.update(padded_plain) + unpadder.finalize()

        return original.decode("utf-8")


# if __name__ == "__main__":
#     secret_key = "NEBULA"
#     salt = "2022"
#     value = ""
#     decrypted = decrypt(secret_key, salt, value)
#     print(f"Decrypted: {decrypted}")
