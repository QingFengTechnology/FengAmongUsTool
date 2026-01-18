# coding: utf-8
from pathlib import Path

# change DEBUG to False if you want to compile the code to exe
DEBUG = "__compiled__" not in globals()


YEAR = 2025
AUTHOR = "QingFeng"
VERSION = "v4.0.0-alpha.2"
APP_NAME = "FengAmongUsTool"
HELP_URL = "https://qfluentwidgets.com"
REPO_URL = "https://github.com/QingFengTechnology/FengAmongUsTool"
FEEDBACK_URL = "https://github.com/QingFengTechnology/FengAmongUsTool/issues"
DOC_URL = "https://qfluentwidgets.com/"

CONFIG_FOLDER = Path('AppData').absolute()
CONFIG_FILE = CONFIG_FOLDER / "config.json"
