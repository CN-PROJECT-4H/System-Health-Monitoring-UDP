import hashlib
import hmac
import random

from dh_params import P, G


def generate_private_key():
    return random.randint(2, P - 2)


def compute_public_key(private_key):
    return pow(G, private_key, P)


def compute_shared_key(peer_public, private_key):
    shared = pow(peer_public, private_key, P)
    return hashlib.sha256(str(shared).encode()).digest()


def create_hmac(key, message):
    return hmac.new(key, message, hashlib.sha256).digest()


def verify_hmac(key, message, received_hmac):
    expected = create_hmac(key, message)
    return hmac.compare_digest(expected, received_hmac)