# Basic file encryption system API

## Installation
First you'll need to set following environment variables:
`MONGODB_FILE_ENCRYPTION_URI` : The URI of the MongoDB instance. 
`BASE_KEY`: The base key used to encrypt the files.
`BASE_MODULUS`: The base modulus used to encrypt the files.

Then you can create a new virtual environment for the client with `python -m venv ./venv` then activate it with `.\venv\Scripts\activate.bat`. You can now install the dependencies with `pip install -r requirements.txt`.