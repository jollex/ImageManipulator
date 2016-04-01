import os

WTF_CSRF_ENABLED = True
SECRET_KEY = '*3AnUKb%GRGaqC1c7CMR'
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
APP_DIR = os.path.join(ROOT_DIR, 'ImageManipulator/')
IMAGE_DIR = os.path.join(APP_DIR, 'static/images/')
SCRIPT_PATH = os.path.join(APP_DIR, 'cli/imagemanipulator.py')
PYTHON = os.path.join(ROOT_DIR, 'env/bin/python')
