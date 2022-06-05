# Basic file encryption system client

## Installation
First you'll need to set following environment variables:
`AZURE_STORAGE_BASE_URL` : The base URL of a file stored in the Azure storage.   
`AZURE_STORAGE_CONNECTION_STRING` : The connection string of the Azure Storage account.  
`AZURE_STORAGE_CONTAINER_NAME` : The name of the Azure Storage container.  
`API_BASE_URL` : The base URL of the API.  
`PRIVATE_COMPONENT`: The private component of the API.  
`PASSWORD_CHARACTERS`: The characters used to generate the password.  
`PASSWORD_SIZE`: The size of the password.  

Then you can create a new virtual environment for the client with `python -m venv ./venv` then activate it with `.\venv\Scripts\activate.bat`. You can now install the dependencies with `pip install -r requirements.txt`.