__all__ = ['logger']


import sys
import http
import click
import logging
from copy import copy
from typing import Optional, Literal


class ColorFormatter(logging.Formatter):
    level_name_colors = {
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="green"),
        logging.INFO: lambda level_name: click.style(str(level_name), fg="bright_cyan"),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="bright_yellow"),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
        logging.CRITICAL: lambda level_name: click.style(str(level_name), fg="bright_red"),
    }

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: Optional[bool] = None,
    ):
        if use_colors in (True, False):
            self.use_colors = use_colors
        else:
            self.use_colors = sys.stdout.isatty()
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name: str, level_no: int) -> str:
        def default(level_name: str) -> str:
            return str(level_name)

        func = self.level_name_colors.get(level_no, default)
        return func(level_name)

    def quick_style(self, value, color):
        return click.style(str(value), fg=color)

    def formatMessage(self, record: logging.LogRecord) -> str:
        recordcopy = copy(record)
        levelname = recordcopy.levelname
        seperator = " " * (8 - len(recordcopy.levelname))
        if self.use_colors:
            levelname = self.color_level_name(levelname, recordcopy.levelno)
            recordcopy.__dict__["process"] = self.quick_style(recordcopy.process, 'magenta')
            if "color_message" in recordcopy.__dict__:
                recordcopy.msg = recordcopy.__dict__["color_message"]
                recordcopy.__dict__["message"] = recordcopy.getMessage()
        recordcopy.__dict__["levelprefix"] = seperator + levelname
        recordcopy.__dict__["location"] = "%30s" % (recordcopy.module + "::" + recordcopy.funcName)
        return super().formatMessage(recordcopy)


class ColorAccessFormatter(ColorFormatter):
    level_name_colors = {
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="green"),
        logging.INFO: lambda level_name: click.style(str(level_name), fg="bright_cyan"),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="bright_yellow"),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
        logging.CRITICAL: lambda level_name: click.style(str(level_name), fg="bright_red"),
    }

    def get_status_code(self, status_code: int):
        try:
            status_phrase = http.HTTPStatus(status_code)
        except ValueError:
            status_phrase = ""

        status_and_phrase = "%s %s" % (status_code, status_phrase)

        if self.use_colors:
            default = lambda code: status_and_phrase
            func = self.level_name_colors.get(status_code // 100, default)

            return func(status_and_phrase)

        return status_and_phrase

    def formatMessage(self, record: logging.LogRecord) -> str:
        recordcopy = copy(record)
        (
            client_addr,
            method,
            full_path,
            http_version,
            status_code,
        ) = recordcopy.args
        status_code = self.get_status_code(int(status_code))
        request_line = "%s %s HTTP/%s" % (method, full_path, http_version)
        if self.use_colors:
            request_line = click.style(request_line, bold=True)

        recordcopy.__dict__.update({
            'client_addr': client_addr,
            'request_line': request_line,
            'status_code': status_code
        })

        return super().formatMessage(recordcopy)


rychlyLogFormatter = ColorFormatter(
    "[{asctime}][{process}][{location}][{levelprefix}]: {message}",
    style='{',
    use_colors=True
)


# The official logger
logger = logging.getLogger("uvicorn")

logger.setLevel("DEBUG")