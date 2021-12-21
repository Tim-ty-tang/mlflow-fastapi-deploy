import hashlib
import os


def md5(file_path):
    """
    Takes a filepath , reads the fie in 4096 byte chunks and update the md5 hash
    :param file_path: str of valid file path
    :return:
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def create_md5_dict(list_of_fname):
    """for a list of file paths, retun the hashed dict"""
    d = {}
    for i in list_of_fname:
        name = os.path.split(i)[1]
        d[name] = md5(i)
    return d
