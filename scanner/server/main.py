#! /home/shadowbadow/python_env/bin/python


from typing import Union
from fastapi import FastAPI
from docs import Docs
import logging
import pathlib
from pydantic import BaseModel


LOGGER = logging.getLogger('uvicorn')


# Get the current directory
curr_dir = pathlib.Path(__file__).parent.absolute()
# Documents directory
files_dir = curr_dir / '..' / 'documents'

LOGGER.info(f'Current Directory: {curr_dir} and Files Directory: {files_dir}')

# Initialize the Docs Object
docs = Docs(files_dir)
LOGGER.info('Initialzed Doc Object')


app = FastAPI()


class ResponseModel(BaseModel):
    message: str
    data: dict = {}


@app.get('/files')
def get_files() -> ResponseModel:
    files = docs.get_formatted_files()
    response = ResponseModel(
        message = 'success',
        data = {'files': files}
    )
    return response


@app.post('/refresh-files')
def refresh_files() -> ResponseModel:
    docs.refresh_files()
    return ResponseModel(message = 'success')
