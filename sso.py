# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "cryptography",
# ]
# ///
import base64
import hmac
import secrets
import unittest
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def build_parameters(parameters: list) -> str:
    # When using encrypted links, the encrypted parameters are BASE64URL
    # encoded for use in the URL. Before encrypting, the parameters can
    # either be defined as a Uniface Gold-Semicolon or ampersand(&) delimited
    # list of values. Depending upon the chosen block cipher mode, an
    # Initialisation Vector (IV) may need appending to the URL parameter
    # as &IV={iv_value} The first step is to define the SSO parameters.
    # If an Initialisation Vector (IV) is being used, this should be added to
    # the URL parameter value. The Initialisation Vector (IV) value should be
    # a random string, as it should be different each time a link is
    # generated
    return "&".join([f"{key}={value}" for key, value in parameters.items()])


def hash_from_built_parameters(built_parameters: str, secret: str) -> bytes:
    # This URL parameter value is then used to generate a hashed message
    # authentication code, using the HMAC-SHA256 algorithm. The key used in
    # generating the HMAC-SHA256 is defined in System Parameter
    # (SYP) ‘SIW_SSO_002’. As the generated hash is a binary value, this is
    # then converted to BASE64…
    return base64.b64encode(
        hmac.digest(secret.encode(), built_parameters.encode(), "sha256")
    )


def build_url_for_encryption(parameters, secret) -> str:
    # …and added to the parameter value, as the HASH parameter
    built_parameters = build_parameters(parameters)
    return f"HASH={hash_from_built_parameters(built_parameters, secret).decode()}&{built_parameters}"


def encrypt_url(url_for_encryption: str, secret: str, iv: str) -> bytes:
    # The URL parameter value is then encrypted using the
    # selected algorithm and cipher block, using the key defined in the System
    # Parameter (SYP) `SIW_SSO_002` and the Initialisation Vector (IV).
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(url_for_encryption.encode())
    padded_data += padder.finalize()
    cipher = Cipher(algorithms.AES(secret.encode()), modes.CBC(iv.encode()))
    encryptor = cipher.encryptor()
    return encryptor.update(padded_data) + encryptor.finalize()


def build_final_url(encrypted_url: bytes, iv: str) -> str:
    # This is then
    # converted to a BASE64, and made URL-safe be converting forward slashes (/) to
    # underscores (\_), and pluses (+) to hyphens (-). The Initialisation Vector
    # (IV) is then appended to the URL as &IV= value, as follows:
    return f"{base64.urlsafe_b64encode(encrypted_url).decode()}&IV={iv}"


def main(parameters, secret):
    iv = parameters["IV"]
    return build_final_url(
        encrypt_url(build_url_for_encryption(parameters, secret), secret, iv), iv
    )


class TestExampleFromManuals(unittest.TestCase):
    def setUp(self):
        self.parameters = {
            "USER": "71562295",
            "PAGE": "PAGECODE",
            "TABS": "N",
            "CREATED": "22 Nov 2019 12:38:44",
            "EXPIRES": "0.5",
            "IV": "B9DC0D86C94B4B15",
        }
        self.secret = "12345678901234567890123412345678"

    def test_build_parameters(self):
        self.assertEqual(
            build_parameters(self.parameters),
            "USER=71562295&PAGE=PAGECODE&TABS=N&CREATED=22 Nov 2019 12:38:44&EXPIRES=0.5&IV=B9DC0D86C94B4B15",
        )

    def test_hash_from_built_parameters(self):
        self.assertEqual(
            hash_from_built_parameters(build_parameters(self.parameters), self.secret),
            "3BjmkdKp+iGLyWb3Xg0UnoF3pCMz1jiJVB8bOxxSKW4=".encode(),
        )

    def test_build_url_for_encryption(self):
        self.assertEqual(
            build_url_for_encryption(self.parameters, self.secret),
            "HASH=3BjmkdKp+iGLyWb3Xg0UnoF3pCMz1jiJVB8bOxxSKW4=&USER=71562295&PAGE=PAGECODE&TABS=N&CREATED=22 Nov 2019 12:38:44&EXPIRES=0.5&IV=B9DC0D86C94B4B15",
        )

    def test_final_url(self):
        iv = self.parameters["IV"]
        self.assertEqual(
            build_final_url(
                encrypt_url(
                    build_url_for_encryption(self.parameters, self.secret),
                    self.secret,
                    iv,
                ),
                iv,
            ),
            "TP5bNR-wJgSWmPiXxxyfkAVlTnxuuMogVP4WX5qd7x4BDOpeVj8v9CZxUCDpTbzun_wE7LxMHSeZnwvItT79m3iI7ZUOp0nhVV3XMHdwy_VyKViUb2GKkQLW7_4F1nCGO_iwnC70nzScgUOdmpQIuHgdlvp-O3yDq67bFycOPl2i_HWdaakLC97mGBr6PEygNgSbi9E6MQSTuQqClNTpoQ==&IV=B9DC0D86C94B4B15",
        )


if __name__ == "__main__":
    parameters = {
        "USER": "MUA_CODE",
        "EXPIRES": "0.01",
        "MAX_USE": "1",
        "IV": secrets.token_hex(8),
    }
    secret = "Value of SYP SIW_SSO_002"
    print(main(parameters, secret))
