#!env/bin/python
import sys
sys.path.insert(0, '/var/www/ImageManipulator')
import logging
logging.basicConfig(stream=sys.stderr)

from ImageManipulator.__init__ import app as application
