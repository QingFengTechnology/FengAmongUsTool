# coding: utf-8
from pathlib import Path

# change DEBUG to False if you want to compile the code to exe
DEBUG = "__compiled__" not in globals()


YEAR = 2025
AUTHOR = "BreezeCrew"
VERSION = "v4.0.0-alpha.3"
VERSION_DATE = "2026-03-06T10:22:48Z"
APP_NAME = "FengAmongUsTool"
HELP_URL = "https://qfluentwidgets.com"
REPO_URL = "https://github.com/BreezeCrew/FengAmongUsTool"
FEEDBACK_URL = "https://github.com/BreezeCrew/FengAmongUsTool/issues"

CONFIG_FOLDER = Path('AppData').absolute()
CONFIG_FILE = CONFIG_FOLDER / "config.json"
