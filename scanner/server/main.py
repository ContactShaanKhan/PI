#! /home/shadowbadow/python_env/bin/python


import os
import sys
from typing import Union
from fastapi import FastAPI, Request
from docs import Docs
from executor import Executor, ScanResolution
from logs import logger as LOGGER
import pathlib
from pydantic import BaseModel


# Ensure the SUDO_PASS ENV Variable is set
if 'SUDO_PASS' not in os.environ:
    LOGGER.error('Must set SUDO_PASS environment variable before running')
    sys.exit(1)


# Get the current directory
curr_dir = pathlib.Path(__file__).parent.absolute()
# Documents directory
files_dir = curr_dir / '..' / 'documents'
# Scripts directory
scripts_dir = curr_dir / '..' / 'scripts'

LOGGER.info(f'Current Directory: {curr_dir} and Files Directory: {files_dir}')


app = FastAPI(
    title='PI Utility API'
)

@app.on_event('startup')
def startup_docs():
    app.docs = Docs(files_dir)


@app.on_event('startup')
def startup_executor():
    app.executor = Executor(scripts_dir, os.environ.get('SUDO_PASS'))


class ResponseModel(BaseModel):
    message: str
    data: dict = {}


@app.get('/files')
def get_files(request: Request) -> ResponseModel:
    ''' Get the files. '''

    files = request.app.docs.get_formatted_files()
    response = ResponseModel(
        message='success',
        data={'files': files}
    )
    return response


@app.post('/refresh-files')
def refresh_files(request:Request) -> ResponseModel:
    ''' Refresh the local file database. Only necessary to run if files are modified manually on the server '''

    request.app.docs.refresh_files()
    return ResponseModel(message='success')


@app.post('/scan/{resolution}/{name}')
def scan_file(
    request: Request,
    name: str,
    resolution: ScanResolution
) -> ResponseModel:
    ''' Scan the document with the specified resolution. '''

    if request.app.docs.file_exists(name):
        return ResponseModel(
            message='failure',
            data={'message': 'file already exists'}
        )

    if (name := request.app.executor.scan(name, resolution)) is None:
        return ResponseModel(message='failure')

    request.app.docs.refresh_files()

    return ResponseModel(
        message='success',
        data={'file': name}
    )


@app.delete('/file/{name}')
def delete_file(
    request: Request,
    name: str
):
    ''' Delete a file by the formatted name. '''

    if (file := request.app.docs.get_file(name)) is None:
        return ResponseModel(
            message='failure',
            data={'message': 'file does not exist'}
        )

    request.app.docs.delete_file(file)

    return ResponseModel(message='success')


if __name__ == '__main__':
    import uvicorn

    LOGGER.info('Running in Production')

    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                '()': 'logs.ColorFormatter',
                'fmt': '[{asctime}][{process}][{location}][{levelprefix}]: {message}',
                'style': '{',
                'use_colors': True,
            },
            'access': {
                '()': 'logs.ColorAccessFormatter',
                'fmt': '[{asctime}][{process}][{location}][{levelprefix}]: {client_addr} = "{request_line}" {status_code}',
                'style': '{',
                'use_colors': True,
            }
        },
        'handlers': {
            'default': {
                'formatter': 'default',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout'
            },
            'access': {
                'formatter': 'access',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            'uvicorn': {'handlers': ['default'], 'level': 'INFO', 'propagate': False},
            'uvicorn.error': {'level': 'INFO'},
            'uvicorn.access': {'handlers': ['access'], 'level': 'INFO', 'propagate': False}
        }
    }

    uvicorn.run('main:app', host='0.0.0.0', port=8000, log_config=log_config)