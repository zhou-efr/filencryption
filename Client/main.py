from datetime import datetime
import os
from dotenv import load_dotenv
from random import randint, sample, seed

from requests import get, post
from pyAesCrypt import encryptFile, decryptFile
from azure.storage.blob import BlobServiceClient


load_dotenv()


PASSWORD_CHARACTERS = os.getenv("PASSWORD_CHARACTERS")
PASSWORD_SIZE = int(os.getenv("PASSWORD_SIZE"))

PRIVATE_COMPONENT = int(os.getenv('PRIVATE_COMPONENT'))

NAME = os.getenv("NAME")


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


def generate_password(user, target, modulus, length, characters):
    password_seed = pow(target['public'], user['private'], modulus)

    seed(password_seed)

    return "".join(sample(characters, length))
    # url = os.getenv("API_BASE_URL") + '/base'
    # base = get(url).json()
    #
    # url = os.getenv("API_BASE_URL") + '/user/' + target
    # target = get(url).json()
    #
    # # password_seed = pow(base['common'], PRIVATE_COMPONENT, base['base'])
    # password_seed = pow(target['public'], PRIVATE_COMPONENT, base['base'])
    #
    # seed(password_seed)
    #
    # return "".join(sample(PASSWORD_CHARACTERS, PASSWORD_SIZE))


def encrypt_file(filename, password):
    encrypted_filename = filename.split('/')[-1] + '.aes'
    encryptFile(filename, encrypted_filename, password)
    return encrypted_filename


def decrypt_file(filename, password, target_directory):
    decrypted_filename = filename[:-4]
    decryptFile(filename, target_directory+'/'+decrypted_filename, password)
    return decrypted_filename


def send_file(
        filename="Grosser_Panda.JPG",
        author={
            'name': os.getenv("NAME"),
            'private': int(os.getenv("PRIVATE_COMPONENT")),
            'public': int(os.getenv("PUBLIC_COMPONENT")),
        },
        recipient={
            'name': os.getenv("NAME"),
            'public': int(os.getenv("PUBLIC_COMPONENT")),
        },
        modulus=int(os.getenv("MODULUS")),
        password_characters=PASSWORD_CHARACTERS,
        password_size=PASSWORD_SIZE,
        file_upload_function=upload_file,
        api_base_url=os.getenv("API_BASE_URL")
):
    password = generate_password(author, recipient, modulus, password_size, password_characters)

    encrypted_filename = encrypt_file(filename, password)
    file_url = file_upload_function(encrypted_filename)
    os.remove(encrypted_filename)

    transfer = {
        "from_user": author['name'],
        "to_user": recipient['name'],
        "cipher": file_url,
        "sendAt": datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    }

    post(api_base_url + '/transfer', json=transfer)


def receive_file(
        transfer={
        "from_user": os.getenv("NAME"),
        "to_user": os.getenv("NAME"),
        "cipher": "https://studentstoragetdttest.blob.core.windows.net/filencryption/06-06-2022-19-28-33-Grosser_Panda.JPG.aes",
        "sendAt": "06-06-2022-19-28-37"
    },
        author={
            'name': os.getenv("NAME"),
            'public': int(os.getenv("PUBLIC_COMPONENT")),
        },
        recipient={
            'name': os.getenv("NAME"),
            'private': int(os.getenv("PRIVATE_COMPONENT")),
        },
        modulus=int(os.getenv("MODULUS")),
        password_characters=PASSWORD_CHARACTERS,
        password_size=PASSWORD_SIZE,
        target_directory=os.getenv("TARGET_DIRECTORY"),
):
    password = generate_password(
        recipient,
        author,
        modulus,
        password_size,
        password_characters
    )

    ciphered_file = get(transfer['cipher'], allow_redirects=True)
    ciphered_filename = transfer['cipher'].split('/')[-1]

    with open(ciphered_filename, "wb") as f:
        f.write(ciphered_file.content)

    decrypt_file(ciphered_filename, password, target_directory)
    os.remove(ciphered_filename)


if __name__ == "__main__":
    # send_file('Grosser_Panda.JPG', "panda")
    # send_file()
    receive_file()
    # url = os.getenv("API_BASE_URL") + '/transfer/' + NAME
    # last_transfer = get(url).json()
    #
    # receive_file(last_transfer, "babin")
    pass
