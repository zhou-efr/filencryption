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


# import all components
# from the tkinter library
import os
from copy import deepcopy
from tkinter import *
from tkinter.messagebox import showinfo, askquestion
from tkinter.ttk import Combobox

# import filedialog module
from tkinter import filedialog, simpledialog

from requests import get

load_dotenv()


def get_user(parent_window):
    def ask_name():
        name = simpledialog.askstring("Name", "What is your name?", parent=parent_window)
        if name is not None:
            try:
                user = get(os.getenv("API_BASE_URL") + '/user/' + name).json()
                return name, user['public']
            except Exception as e:
                showinfo("Error", e)
                return ask_name()
        else:
            return None, None

    user_name, public_key = ask_name()
    if user_name is None or public_key is None:
        return None

    def ask_private_component(public_component):
        private_component = simpledialog.askinteger("Private component", "What is your private component?", parent=parent_window)
        if private_component is not None:
            try:
                base = get(os.getenv("API_BASE_URL") + '/base').json()
                if pow(base['common'], private_component, base['base']) == public_component:
                    return private_component
                else:
                    showinfo("Error", "The private component is not valid")
                    return ask_private_component(public_component)
            except Exception as e:
                showinfo("Error", e)
                return ask_private_component(public_component)
        else:
            return None

    private_comp = ask_private_component(public_key)
    if private_comp is None:
        return None

    return {
        "name": user_name,
        "private": private_comp,
        "public": public_key
    }


class SendFrame(Frame):
    def __init__(self, master, users, user):
        super().__init__(master)
        self.author = user
        self.label_file_explorer = Label(
            self,
            text="Grosser_Panda.JPG",
            width=100, height=4,
            fg="blue")
        self.label_file_explorer.pack()

        self.label_connected_as = Label(
            self,
            text="connected as: " + self.author['name'],
            width=100, height=4,
            fg="blue")
        self.label_connected_as.pack()

        self.combo_box_users = Combobox(
            self,
            values=list(users.keys()))
        self.combo_box_users.pack()

        self.button_explore = Button(
            self,
            text="Browse Files",
            command=self.handle_browse_files)
        self.button_explore.pack()

        self.button_send = Button(
            self,
            text="Send File",
            command=self.handle_send_file)
        self.button_send.pack()

    def handle_browse_files(self):
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select a File",
            filetypes=(("Image Files", "*.jpg"), ("All Files", "*.*")))

        # Change label contents
        self.label_file_explorer.configure(text=filename)

    def handle_send_file(self):
        author = {
            "name": self.author['name'],
            "private": self.author['private'],
            "public": self.author['public']
        }
        target = get(os.getenv("API_BASE_URL") + '/user/' + self.combo_box_users.get()).json()
        send_file(self.label_file_explorer.cget("text"), author, target)


class MailboxFrame(Frame):
    def __init__(self, master, transfers, user):
        super().__init__(master)
        self.recipient = user
        self.label_connected_as = Label(
            self,
            text="connected as: " + self.recipient['name'],
            width=100, height=4,
            fg="blue")
        self.label_connected_as.pack()
        self.transfers = list(filter(lambda x: x['to_user'] == self.recipient['name'], transfers))
        self.button_transfers = []
        for index, transfer in enumerate(self.transfers):
            print(index)
            self.button_transfers.append(Button(
                self,
                text=transfer['from_user'] + " at " + transfer['sendAt'],
                command=lambda i=index: self.handle_receive_file(i)))
            self.button_transfers[-1].pack()

    def handle_receive_file(self, button_index):
        try:
            author = get(os.getenv("API_BASE_URL") + '/user/' + self.transfers[button_index]['from_user']).json()
            receive_file(transfer=self.transfers[button_index], author=author, recipient=self.recipient)
            # self.button_transfers[button_index].destroy()
        except Exception as e:
            showinfo("Error", e)

        showinfo("Success", "File received")


class FilencryptionWindow(Tk):
    def __init__(self, user):
        super().__init__()

        self.user = user

        self.title("File Encryption")
        self.geometry("700x500")
        self.config(background="white")

        menubar = Menu(self)

        encryption = Menu(menubar, tearoff=0)
        encryption.add_command(label="Send", command=self.show_send_frame)
        encryption.add_command(label="Mail box", command=self.show_mailbox_frame)
        encryption.add_separator()
        encryption.add_command(label="Quitter", command=self.quit)
        menubar.add_cascade(label="filencryption", menu=encryption)

        self.config(menu=menubar)

        self.container = Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_send_frame()

        self.user = get_user(self)
        if self.user is None:
            self.quit()

        self.show_send_frame()

    def show_send_frame(self):
        print("show_send_frame")
        users = get(os.getenv("API_BASE_URL") + '/users/').json()
        users_dict = {}
        for user in users['users']:
            users_dict[user['name']] = user['public']
        print("users received")
        frame = SendFrame(self.container, users_dict, self.user)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def show_mailbox_frame(self):
        print("show_mailbox_frame")
        transfers = get(os.getenv("API_BASE_URL") + '/transfers/').json()['transfers']
        print("transfers received")
        frame = MailboxFrame(self.container, transfers, self.user)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()


def load_ui(users, transfers):
    def alert():
        showinfo("alerte", "Bravo!")

    # Create the root window
    window = Tk()

    menubar = Menu(window)

    encryption = Menu(menubar, tearoff=0)
    encryption.add_command(label="Send", command=lambda: SendFrame(window, users).tkraise())
    encryption.add_command(label="Mail box", command=lambda: MailboxFrame(window, transfers).tkraise())
    encryption.add_separator()
    encryption.add_command(label="Quitter", command=window.quit)
    menubar.add_cascade(label="filencryption", menu=encryption)

    window.config(menu=menubar)

    # Set window title
    window.title('File Explorer')

    # Set window size
    window.geometry("700x500")

    # Set window background color
    window.config(background="white")

    # Create a frame
    # frame = SendFrame(window, users)
    frame = MailboxFrame(window, transfers)
    frame.pack(padx=30, pady=30)

    # Let the window wait for any events
    window.mainloop()


def main():
    user = {
        "name": os.getenv("NAME"),
        "private": int(os.getenv("PRIVATE_COMPONENT")),
        "public": int(os.getenv("PUBLIC_COMPONENT"))
    }
    app = FilencryptionWindow(user)
    app.mainloop()


if __name__ == "__main__":
    main()
