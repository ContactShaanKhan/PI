from logs import logger as LOGGER
from enum import IntEnum
import subprocess
import logging
import shlex


class ScanResolution(IntEnum):
    LOW = 300
    MEDIUM = 600
    HIGH = 900


class Executor():

    def __init__(self, scripts_dir, sudo_pass):
        self.scripts_dir = scripts_dir
        self.sudo_pass = sudo_pass

    def run(self, command, capture_output=False, shell=False, sudo=False):
        if sudo:
            command = f'echo {self.sudo_pass} | sudo -S {command}'
            shell = True

        formatted_command = shlex.split(command) if not shell else command
        try:
            res = subprocess.run(formatted_command, capture_output=capture_output, check=True, shell=shell)
            return res

        except subprocess.CalledProcessError:
            LOGGER.warning(f'Command {command} failed.')
            return None

    def scan(self, name, resolution):
        script = str(self.scripts_dir / 'scan.sh')
        command = f'{script} --name {name} --resolution {resolution.value}'

        LOGGER.info(f'Scanning with command {command}')

        if self.run(command, sudo=True) is not None:
            return f'{name}.jpg'

        return None
