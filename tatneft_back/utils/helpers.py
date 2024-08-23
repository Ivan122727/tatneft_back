import os
import zipfile
from typing import Any

from tatneft_back.core.settings import STATIC_DIRPATH


class NotSet:
    pass


def is_set(v: Any) -> bool:
    return not (v is NotSet or isinstance(v, NotSet))


class SetForClass:
    @classmethod
    def set(cls) -> set[str]:
        keys = list(cls.__dict__.keys())
        res = {
            cls.__dict__[k]
            for k in keys
            if isinstance(k, str) and not k.startswith('__') and not k.endswith('__') and k != 'set'
        }
        return res


def zipdir(dirpath: str, zip_filepath: str):
    with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                zip_file.write(os.path.join(root, file),
                               os.path.relpath(os.path.join(root, file),
                                               os.path.join(dirpath, '..')))
                
def create_zip_archive(file_paths, zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in file_paths:
            # Имя файла внутри архива (без пути)
            arcname = os.path.basename(file_path)

            # Добавление файла в архив
            zip_file.write(file_path, arcname=arcname)

    return zip_file_path
