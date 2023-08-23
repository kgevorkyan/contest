from glob import glob
from enum import Enum
import subprocess
import datetime
import os


class Build(Enum):
    CMAKE = "CMake"
    FILES = "files"
    CONF = "configure"


def create_dir(path: str) -> str:
    if os.path.exists(path):
        path = os.path.join(os.path.dirname(path), datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S_") + "result")

    os.makedirs(path)
    return path


def get_c_files_str(path_to: str) -> str:
    c_files = [y for x in os.walk(path_to) for y in glob(os.path.join(x[0], "*.c"))]
    if not c_files:
        print("No '*.c' file found in directory:", path_to)
        return ""

    return to_str(c_files)


def to_str(tmp: list) -> str:
    res = " "
    for i in tmp:
        res += i + " "

    return res


def run_cmd(command: str, dir_to_run=os.getcwd()) -> None:
    exit_code = subprocess.call(command, shell=True, cwd=dir_to_run)
    if exit_code != 0:
        raise RuntimeError(command + "\nFailure with exit code: " + str(exit_code))
