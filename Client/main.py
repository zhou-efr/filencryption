from datetime import datetime
import os
from random import randint, sample, seed

from requests import get, post
from pyAesCrypt import encryptFile, decryptFile
from azure.storage.blob import BlobServiceClient


PASSWORD_CHARACTERS = os.getenv("PASSWORD_CHARACTERS")
PASSWORD_SIZE = int(os.getenv("PASSWORD_SIZE"))

PRIVATE_COMPONENT = int(os.getenv('PRIVATE_COMPONENT'))

NAME = "panda"


def upload_file(filename):
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
    blob_name = datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + '-' + filename
    blob_client = blob_service_client.get_blob_client(
        container=os.getenv("AZURE_STORAGE_CONTAINER_NAME"),
        blob=blob_name
    )
    with open(filename, "rb") as data:
        blob_client.upload_blob(data)

    return os.getenv("AZURE_STORAGE_BASE_URL") + '/' + blob_name


def generate_password(target):
    url = os.getenv("API_BASE_URL") + '/base'
    base = get(url).json()

    url = os.getenv("API_BASE_URL") + '/user/' + target
    target = get(url).json()

    # password_seed = pow(base['common'], PRIVATE_COMPONENT, base['base'])
    password_seed = pow(target['public'], PRIVATE_COMPONENT, base['base'])

    seed(password_seed)

    return "".join(sample(PASSWORD_CHARACTERS, PASSWORD_SIZE))


def encrypt_file(filename, password):
    encrypted_filename = filename + '.aes'
    encryptFile(filename, encrypted_filename, password)
    return encrypted_filename


def decrypt_file(filename, password):
    decrypted_filename = filename[:-4]
    decryptFile(filename, decrypted_filename, password)
    return decrypted_filename


def send_file(filename, target):
    password = generate_password(target)

    encrypted_filename = encrypt_file(filename, password)
    file_url = upload_file(encrypted_filename)
    os.remove(encrypted_filename)

    transfer = {
        "from_user": NAME,
        "to_user": target,
        "cipher": file_url,
        "sendAt": datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    }

    post(os.getenv("API_BASE_URL") + '/transfer', json=transfer)


def receive_file(transfer, author):
    password = generate_password(author)

    ciphered_file = get(transfer['cipher'], allow_redirects=True)
    ciphered_filename = transfer['cipher'].split('/')[-1]

    with open(ciphered_filename, "wb") as f:
        f.write(ciphered_file.content)

    decrypt_file(ciphered_filename, password)
    os.remove(ciphered_filename)


if __name__ == "__main__":
    send_file('Grosser_Panda.JPG', "panda")

    url = os.getenv("API_BASE_URL") + '/transfer/' + NAME
    last_transfer = get(url).json()

    receive_file(last_transfer, "panda")
    pass
