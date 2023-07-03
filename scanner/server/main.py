#! /home/shadowbadow/python_env/bin/python


from typing import Union
from fastapi import FastAPI, Request
from docs import Docs
from executor import Executor, ScanResolution
from logs import logger as LOGGER
import pathlib
from pydantic import BaseModel


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
    app.executor = Executor(scripts_dir)


class ResponseModel(BaseModel):
    message: str
    data: dict = {}


@app.get('/files')
def get_files(request: Request) -> ResponseModel:
    files = request.app.docs.get_formatted_files()
    response = ResponseModel(
        message='success',
        data={'files': files}
    )
    return response


@app.post('/refresh-files')
def refresh_files(request:Request) -> ResponseModel:
    request.app.docs.refresh_files()
    return ResponseModel(message='success')


@app.post('/scan/{resolution}/{name}')
def scan_file(
    request: Request,
    name: str,
    resolution: ScanResolution
) -> ResponseModel:
    if (name := request.app.executor.scan(name, resolution)) is None:
        return ResponseModel(message='failure')

    request.app.docs.refresh_files()

    return ResponseModel(
        message='success',
        data={'file': name}
    )



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