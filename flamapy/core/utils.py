import os.path


def extract_filename_extension(filename: str) -> str:
    return filename.rsplit(".", maxsplit=1)[-1]


def file_exists(filepath: str) -> bool:
    return os.path.isfile(filepath)
