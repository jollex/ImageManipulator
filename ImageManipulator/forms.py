from flask_wtf import Form
from wtforms import FileField, RadioField, StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import StopValidation, DataRequired

import imghdr

class ImageFileRequired(object):
    """
    Validates that an uploaded file from a flask_wtf FileField is, in fact an
    image.  Better than checking the file extension, examines the header of
    the image using Python's built in imghdr module.

    Author: https://gist.github.com/msukmanowsky/8086892
    """
    def __init__(self, message=None):
        self.message = message or u'An image file is required'

    def __call__(self, form, field):
        if (field.data is None
            or imghdr.what('unused', field.data.read()) is None):
            raise StopValidation(self.message)

        field.data.seek(0)

class ImageManipulationForm(Form):
    image = FileField('image',
        validators=[ImageFileRequired(message='You must upload an image file')])

    animation = RadioField('animation',
        choices=[('auto', 'GIF'),
                 ('one_frame', 'One Frame'),
                 ('custom', 'Custom')],
        default='auto')
    box_size = StringField('box_size')
    frames = StringField('frames')
    save_frames = BooleanField('save_frames')

    box_shape = RadioField('box_shape',
        choices=[('square', 'Square'),
                 ('vertical', 'Vertical slices'),
                 ('horizontal', 'Horizontal slices')],
        default='square')

    rotation = SelectField('rotation',
        choices=[('none', 'None'),
                 ('flip', 'Flip'),
                 ('ninety', 'Multiples of 90 degrees')])
    randomize = BooleanField('randomize')
    average = BooleanField('average')

    submit = SubmitField('Submit')
