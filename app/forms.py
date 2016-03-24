from flask.ext.wtf import Form
from wtforms import FileField, validators

import imghdr

class ImageFileRequired(object):
    """
    Validates that an uploaded file from a flask_wtf FileField is, in fact an
    image.  Better than checking the file extension, examines the header of
    the image using Python's built in imghdr module.

    Author: https://gist.github.com/msukmanowsky/8086892
    """
    def __init__(self, message=None):
        self.message = message or u'Field must be an image file.'

    def __call__(self, form, field):
        if field.data is None or imghdr.what('unused', field.data.read()) is None:
            message = self.message or 'An image file is required'
            raise validators.StopValidation(message)

        field.data.seek(0)

class ImageManipulationForm(Form):
    image = FileField('image', validators=[ImageFileRequired()])
