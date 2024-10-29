import configparser
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
import base64

class Author:
    """
    Author class to manage author information and related operations.
    Attributes:
        full_name (str): Full name of the author.
        short_name (str): Short name or nickname of the author.
        email (str): Email address of the author.
        phone (str): Phone number of the author.
        mobile_phone (str): Mobile phone number of the author.
        role (str): Role or title of the author.
        extra_info1 (str): Additional information field 1.
        extra_info2 (str): Additional information field 2.
        extra_info3 (str): Additional information field 3.
        extra_info4 (str): Additional information field 4.
        extra_info5 (str): Additional information field 5.
    Methods:
        __init__(self, full_name, short_name, email, phone, mobile_phone, role, extra_info1, extra_info2, extra_info3, extra_info4, extra_info5):
            Initializes an Author instance with the provided attributes.
        to_dict(self):
            Converts the Author instance to a dictionary format.
        save(self, config):
            Saves the Author instance to an INI file in the specified directory.
        encrypt_signature(signature_path, password):
            Encrypts the signature file using the provided password.
        decrypt_signature(encrypted_signature_path, password, salt):
            Decrypts the encrypted signature file using the provided password and salt.
        load(short_name, config):
            Loads an Author instance from an INI file based on the short name.
        delete(short_name, config):
            Deletes the Author's INI file, signature file, and salt file based on the short name.
    """
    def __init__(self, full_name, short_name, email, phone, mobile_phone, role,
                 extra_info1, extra_info2, extra_info3, extra_info4, extra_info5):
        self.full_name = full_name
        self.short_name = short_name
        self.email = email
        self.phone = phone
        self.mobile_phone = mobile_phone
        self.role = role
        self.extra_info1 = extra_info1
        self.extra_info2 = extra_info2
        self.extra_info3 = extra_info3
        self.extra_info4 = extra_info4
        self.extra_info5 = extra_info5

    def to_dict(self):
        return {
            'SignerFullName': self.full_name,
            'SignerName': self.full_name,
            'SignerShortName': self.short_name,
            'SignerEmail': self.email,
            'SignerPhone': self.phone,
            'SignerMobilePhone': self.mobile_phone,
            'SignerCell': self.mobile_phone,
            'SignerRole': self.role,
            'SignerExtraInfo1': self.extra_info1,
            'SignerExtraInfo2': self.extra_info2,
            'SignerExtraInfo3': self.extra_info3,
            'SignerExtraInfo4': self.extra_info4,
            'SignerExtraInfo5': self.extra_info5
        }



    def save(self, config):
        signers_dir = config.get_signers_dir()
        ini_path = os.path.join(signers_dir, f"Signer-{self.short_name}.ini")

        author_config = configparser.ConfigParser()
        author_config['Author'] = self.to_dict()

        with open(ini_path, 'w', encoding='utf-8') as configfile:
            author_config.write(configfile)

    @staticmethod
    def encrypt_signature(signature_path, password):
        with open(signature_path, 'rb') as file:
            signature_data = file.read()

        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        fernet = Fernet(key)
        encrypted_signature = fernet.encrypt(signature_data)
        return salt, encrypted_signature

    @staticmethod
    def decrypt_signature(encrypted_signature_path, password, salt):
        with open(encrypted_signature_path, 'rb') as file:
            encrypted_signature = file.read()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        fernet = Fernet(key)
        try:
            decrypted_signature = fernet.decrypt(encrypted_signature)
            return decrypted_signature
        except Exception:
            return None

    @staticmethod
    def load(short_name, config):
        signers_dir = config.get_signers_dir()
        ini_path = os.path.join(signers_dir, f"Signer-{short_name}.ini")

        if not os.path.exists(ini_path):
            return None

        author_config = configparser.ConfigParser()
        author_config.read(ini_path, encoding='utf-8')

        author_data = author_config['Author']

        return Author(
            full_name=author_data['SignerFullName'],
            short_name=author_data['SignerShortName'],
            email=author_data['SignerEmail'],
            phone=author_data['SignerPhone'],
            mobile_phone=author_data['SignerMobilePhone'],
            role=author_data['SignerRole'],
            extra_info1=author_data['SignerExtraInfo1'],
            extra_info2=author_data['SignerExtraInfo2'],
            extra_info3=author_data['SignerExtraInfo3'],
            extra_info4=author_data['SignerExtraInfo4'],
            extra_info5=author_data['SignerExtraInfo5']
        )

    @staticmethod
    def delete(short_name, config):
        signers_dir = config.get_signers_dir()
        ini_path = os.path.join(signers_dir, f"Signer-{short_name}.ini")
        signature_path = os.path.join(signers_dir, f"Signer-{short_name}-Signature.png")
        salt_path = os.path.join(signers_dir, f"Signer-{short_name}-Salt.bin")

        if os.path.exists(ini_path):
            os.remove(ini_path)

        if os.path.exists(signature_path):
            os.remove(signature_path)

        if os.path.exists(salt_path):
            os.remove(salt_path)
