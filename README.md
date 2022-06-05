# Basic file encryption system

## Presentation
This is a basic e2ee encryption system. It is based on the [AES-256-GCM](https://en.wikipedia.org/wiki/Galois/Counter_Mode) algorithm.

The concept is to encrypt a file with a random password generated with a seed. This seed is created from the private key of the sender and the public key of the receiver following [Diffie-Hellman](https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange) secret key exchange process.

The API store publicly the public key of all user and the file transfers in a MongoDB database.