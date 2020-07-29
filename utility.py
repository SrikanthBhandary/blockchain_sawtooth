import hashlib
import constants
import secp256k1


def generate_hash(string):
    """
    :string any input string will be encoded and hex digest will be returned
    """
    return hashlib.sha512(string.encode('utf-8')).hexdigest()

def generate_address(public_key):
    address_first_part = generate_hash(constants.FAMILY_NAME)
    address_second_part = generate_hash(public_key)
    return address_first_part[0:6] + address_second_part[0:64]

def generate_keys():
    key_handler = secp256k1.PrivateKey()
    print("Public Key", key_handler.pubkey.serialize().hex())
    print("Private Key", key_handler.private_key.hex())
    return key_handler.pubkey.serialize().hex(), key_handler.private_key.hex()


public_key = "0249be75d67ec334b560a9dbee203995d4d42c049194ae8ee6cc023f833593bced"
private_key = "948f71a08c4c7b68cedaca2e667265ca8e27734dd9eaeecda4ed6b130196cc7b"
