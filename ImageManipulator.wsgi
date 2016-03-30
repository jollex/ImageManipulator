#!env/bin/python
activate_this = '/var/www/ImageManipulator/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this)

import sys
sys.path.insert(0, '/var/www/ImageManipulator')
import logging
logging.basicConfig(stream=sys.stderr)

from ImageManipulator.__init__ import app as application
