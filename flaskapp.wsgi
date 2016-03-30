#!env/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/ImageManipulator/")

from ImageManipulator import app
