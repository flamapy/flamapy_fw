import os.path


def extract_filename_extension(filename: str) -> str:
    return filename.rsplit(".", maxsplit=1)[-1]


def filename_matches_extension(filename: str, extension: str) -> bool:
    """Whether the filename ends with the given extension.

    Supports compound extensions such as 'uvl.json'.
    """
    return filename.endswith(f".{extension}")


def file_exists(filepath: str) -> bool:
    return os.path.isfile(filepath)
