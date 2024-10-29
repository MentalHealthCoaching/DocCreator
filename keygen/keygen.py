from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_key_pair(public_key_path, private_key_path, passphrase):
    """
    Generates a pair of RSA keys (public and private) and saves them to the specified file paths.
    Args:
        public_key_path (str): The file path where the public key will be saved.
        private_key_path (str): The file path where the private key will be saved.
        passphrase (str): The passphrase used to encrypt the private key.
    Returns:
        None
    """
    # Generate a private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    # Encrypt and save the private key using the provided passphrase
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(passphrase.encode())
    )

    with open(private_key_path, 'wb') as f:
        f.write(pem)

    # Save the public key without encryption
    with open(public_key_path, 'wb') as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

if __name__ == '__main__':
    passphrase = input("Enter a passphrase to secure your private key: ")
    generate_key_pair('keys/public_key.pem', 'keys/private_key.pem', passphrase)
