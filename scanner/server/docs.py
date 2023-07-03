import pathlib


class Docs():

    def __init__(self, files_dir):
        self.files_dir = files_dir
        self.refresh_files()

    def refresh_files(self):
        files = [f for f in self.files_dir.iterdir() if f.is_file()]
        self.files = files

    def get_formatted_files(self):
        files = [str(f).split('/')[-1] for f in self.files]
        return files

    def __str__(self):
        return str(self.get_formatted_files())

