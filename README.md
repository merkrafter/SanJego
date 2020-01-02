![](https://github.com/merkrafter/SanJego/workflows/.github/workflows/pythonapp.yml/badge.svg?branch=development)

# SanJego
This project examines the game of San Jego. Information on how this game works can be found in the project's wiki.

## Getting started
These instructions help you set up this project on your local machine to either experiment with the source code or just get results.

### Prerequisites
In order to develop this project you will need a Python 3 installation (only 3.7 and 3.8 were tested).
If you only want to create some results, then Docker is the preferred way.

### Installation
To set up the development environment, the following steps are recommended. These are bash commands and may differ on Windows.
```bash
git clone https://github.com/merkrafter/SanJego # get sources
cd SanJego
python -m venv venv # create virtual environment in order to isolate from other python installations
source venv/bin/activate # venv/Script/activate under Windows
pip install -r requirements.txt
```

Using Docker all you need to do is get the image.

## Running the tests
*NOTE*: The tests are not included in the Docker image.

### Functional tests
This command triggers the functional tests:
```bash
python -m pytest -m "not slow" test/* # the -m "not slow" may be omitted to run ALL tests; this will possibly take multiple minutes
```

### Code style tests
This command triggers the code style tests:
```bash
flake8 --per-file-ignores="main.py:F841" --max-line-length=120 --statistic src/
```
main.py utilizes the sacred library whose `config` function triggers unused variable errors (F841) but is totally fine.

## Deployment
The python application can be started with
```bash
python main.py [with <override arguments>]
python main.py with height=2 width=3 # as an example
```

The Docker container can be created with
```bash
docker run \
 -it \ # to see program output directly
 --rm \ # if you wish to delete the container afterwards
 -e HEIGHT=2 \ # override arguments by specifying environment variables
 -e WIDTH=3 \
 -v sanjego-results:/home/sanjego/results \ # volume to store the experiment results
 merkrafter/sanjego # the image name
```

## Built with
- [Python](https://www.python.org/)
- [pip](https://pip.pypa.io/en/stable/) -- dependency management for python
- [sacred](https://sacred.readthedocs.io/en/stable/) -- experiment framework

## Contributing
As this is a study project you may not provide code improvements directly. Still, issues are very welcome to suggest improvements and show errors.

## License
This project is licensed under the GNU GPL - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgements
This README was created from this [template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2).
