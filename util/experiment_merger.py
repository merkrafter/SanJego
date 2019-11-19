import argparse
import glob
import itertools
import os
import shutil
import sys
from typing import List, Dict, Optional

from util.experiments_adapter import ExperimentsAdapter


def get_files(dir_name: str) -> List[Dict]:
    ea = ExperimentsAdapter(dir_name)
    return list(ea)


def find_corresponding_file(exp_file: Dict, in_dir: List) -> Optional[Dict]:
    """
    Finds the *first* experiment in the directory called `in_dir` which has the same configuration data as `exp_file`
    has.
    :param exp_file: experiment data as returned by `get_files`
    :param in_dir: a list of experiment data as returned by `get_files`
    :return: experiment data that has the same config as `exp_file` or `None` if there is no such experiment
    """
    try:
        return next(filter(lambda exp: exp['config'] == exp_file['config'], in_dir))
    except StopIteration:  # in case the above filter is empty
        return None


def move_to(target_dir: str, exp_file: Dict) -> None:
    """
    Moves the experiment file to the target_dir by choosing the lowest free number as the new experiment name
    :param target_dir: target directory
    :param exp_file: the experiment data to move
    """
    existing_file_names = glob.glob(f"{target_dir}/*")
    for new_name in itertools.count(1):
        if str(new_name) not in map(os.path.basename, existing_file_names):
            break
    print(f"{exp_file['filename']} -> {target_dir}/{new_name}")
    shutil.move(exp_file['filename'], f"{target_dir}/{new_name}")


def safely_move_file(from_file: Dict, to_file: Dict) -> None:
    """
    Given two existing files, rename `to_file` to `to_file.backup` and `from_file` to `to_file`.
    :param from_file: file to be moved
    :param to_file: destination for moving `from_file`
    """
    to_file = to_file['filename']
    to_file_backup = to_file
    while os.path.exists(to_file_backup):
        to_file_backup += ".backup"

    print(f"{to_file} -> {to_file_backup}")
    shutil.move(to_file, to_file_backup)
    print(f"{from_file['filename']} -> {to_file}")
    shutil.move(from_file['filename'], to_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("SOURCE", help="files in this folder are moved")
    parser.add_argument("TARGET", help="the directory all files are merged into")
    parser.add_argument("-o", "--override", help="overwrite experiments in target directory; default: store backups",
                        action="store_true")

    namespace = parser.parse_args()

    # error handling
    if not os.path.isdir(namespace.TARGET):
        sys.stderr.write(f"Not a directory: {namespace.TARGET}\n")

    if not os.path.isdir(namespace.SOURCE):
        sys.stderr.write(f"Not a directory: {namespace.SOURCE}\n")

    if not namespace.TARGET == namespace.SOURCE:
        target_files = get_files(namespace.TARGET)
        source_files = get_files(namespace.SOURCE)
        for file in source_files:
            corresponding_file = find_corresponding_file(file, in_dir=target_files)
            if not corresponding_file:
                move_to(namespace.TARGET, file)
            else:
                safely_move_file(from_file=file, to_file=corresponding_file)
