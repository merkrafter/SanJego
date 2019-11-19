import argparse
import glob
import os
import sys
from typing import List, Dict

from util.experiments_adapter import ExperimentsAdapter


def get_files(dir_name: str) -> List[Dict]:
    ea = ExperimentsAdapter(dir_name)
    return list(ea)


def find_corresponding_file(file: Dict, in_dir: List) -> Dict:
    try:
        return in_dir[in_dir.index(file)]  # won't work like this; need comparison of configs
    except ValueError:
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("SOURCE", help="files in this folder are moved")
    parser.add_argument("TARGET", help="the directory all files are merged into")
    parser.add_argument("-o", "--override", help="overwrite experiments in target directory; default: store backups",
                        action="storeTrue")

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
                move_to(target_files, file)
            else:
                safely_move_file(
                from=file, to = corresponding_file)

                print(namespace)
