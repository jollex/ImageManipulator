from flask.ext.wtf import Form
from wtforms import FileField, RadioField, StringField, SelectField, BooleanField, SubmitField, validators

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

    # TODO: Add configuration options.

    # Animation options:
    # Auto | One Frame | Custom
    # Box size slider
    # Number of frames slider
    # If One Frame is selected, show box size slider field
    # If Custom is selected, show box size and number of frames sliders
    animation = RadioField('animation', choices=[('auto', 'Automatic'),
        ('one_frame', 'One Frame'), ('custom', 'Custom')])
    box_size = StringField('box_size')
    frames = StringField('frames')

    # Box shape options:
    # Square | Vertical | Horizontal
    box_shape = RadioField('box_shape', choices=[('square', 'Square'),
        ('vertical', 'Vertical slices'), ('horizontal', 'Horizontal slices')])

    # Effects:
    # Rotation drop down menu: [None, Flip, Multiple of 90]; doesn't show
    # Multiples of 90 if vertical or horizontal are selected.
    # Randomize boxes checkbox
    # Average boxes checkbox
    rotation = SelectField('rotation', choices=[('none', 'None'), ('flip', 'Flip'), ('ninety', 'Multiples of 90 degrees')])
    randomize = BooleanField('randomize')
    average = BooleanField('average')

    submit = SubmitField('Submit')
