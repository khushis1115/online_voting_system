from cryptography.fernet import Fernet
import hashlib

# Generate a key for encryption and decryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)


def submit_vote(vote_data):
    # Encrypt vote using AES
    encrypted_vote = cipher_suite.encrypt(vote_data.encode())

    # Create a SHA-256 hash of the encrypted vote
    vote_hash = hashlib.sha256(encrypted_vote).hexdigest()

    return {'encrypted_vote': encrypted_vote, 'vote_hash': vote_hash}