import pathlib
from logs import logger as LOGGER

class Docs():

    def __init__(self, files_dir):
        self.files_dir = files_dir
        self.refresh_files()

    def refresh_files(self):
        files = [f for f in self.files_dir.iterdir() if f.is_file()]
        files = [f for f in files if '.gitkeep' not in str(f)]

        self.files = files

    def file_exists(self, name):
        f = self.get_file(name)
        return f is not None

    def get_file(self, name):
        ''' By default, search by the formatted file name '''

        formatted_files = self.get_formatted_files()
        for f, formatted_name in zip(self.files, formatted_files):
            if name == formatted_name:
                return f
        return None

    def get_file_by_full_name(self, name):
        for f in self.files:
            if name == str(f):
                return f

    def delete_file(self, file):
        LOGGER.info(f'Deleting file {str(file)}')
        file.unlink()
        self.refresh_files()

    def get_formatted_files(self):
        files = [str(f).split('/')[-1] for f in self.files]
        return files

    def __str__(self):
        return str(self.get_formatted_files())
