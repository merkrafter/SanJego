import glob
import json
import re
from pprint import pprint

from typing import Dict, Iterator


def load_experiments(dir_name: str) -> Iterator[str]:
    """
    Returns an iterator over exp_file names of experiments that reside under `DIR_NAME`.
    The order of elements may be arbitrary.
    :param dir_name: the directory that holds the experiments
    :return: an iterator over experiment exp_file names
    """
    return [exp for exp in glob.glob(f"{dir_name}/*") if
            not (exp.endswith("_sources") or exp.endswith("backup"))].__iter__()


def load_experiment_json(subfile: str) -> Dict:
    """
    Uses the `json` module to read the contents of the exp_file `subfile`
    :param subfile: json exp_file
    :return: python dictionary built from `subfile`
    """
    with open(subfile, 'r') as f:
        return json.load(f)


def read_cout(subfile: str) -> Dict:
    """
    Reads the cout.txt exp_file of an experiment and returns a dict with the following keys:
     - nr_nodes (int) number of nodes searched
    This function heavily depends on the output given by the main program.
    :param subfile: path to the cout.txt exp_file (including the exp_file name)
    :return: dict with extracted information
    """
    node_regex = re.compile("Searched (\d+) nodes")

    with open(subfile, 'r') as f:
        for line in f:
            m = node_regex.match(line)
            if m:
                nr_nodes = int(m.group(1))

    return {'nr_nodes': nr_nodes}


class ExperimentsAdapter(object):
    """
    This class reads the experiment data created by sacred and provides it as an iterator.
    The methods of this class assume that the experiment results directory is not changed after an object is created.
    """

    def __init__(self, dir_name: str) -> None:
        """
        Creates a new ExperimentsAdapter that provides access to a sacred results directory.
        :param dir_name: a path to a folder that holds sacred experiment results
        """
        self.dir_name = dir_name
        self.experiments = load_experiments(dir_name)

    def reload(self) -> None:
        """
        Resets the iterator over the files in the given directory.
        """
        self.experiments = load_experiments(self.dir_name)

    def __iter__(self) -> Iterator[Dict]:
        return self

    def __next__(self) -> Dict:
        """
        Iterates over the dicts given by the experiment files.
        :return: dict with keys filename, config, cout, metrics and run
        """
        experiment = next(self.experiments)
        return {
            'filename': experiment,
            'config': load_experiment_json(f"{experiment}/config.json"),
            'cout': read_cout(f"{experiment}/cout.txt"),
            'metrics': load_experiment_json(f"{experiment}/metrics.json"),
            'run': load_experiment_json(f"{experiment}/run.json")
        }


if __name__ == '__main__':
    DIR_NAME = "../results"
    adapter = ExperimentsAdapter(DIR_NAME)
    for experiment_result in adapter:
        pprint(experiment_result)
