import os
from flask import render_template, send_from_directory
from app import app
from .forms import ImageManipulationForm
from werkzeug import secure_filename

@app.route('/', methods=['GET', 'POST'])
def start():
    form = ImageManipulationForm()

    if form.validate_on_submit():
        filename = secure_filename(form.image.data.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        form.image.data.save(file_path)

        gif, images = manipulate_image(file_path, form)
        return render_template('result.html', gif=gif, images=images)

    return render_template('index.html', form=form)

@app.route('/output/<path:filename>')
def send_file(filename):
    root_dir = os.path.dirname(__file__)
    return send_from_directory(os.path.join(root_dir,
        app.config['OUTPUT_FOLDER']), filename)

def manipulate_image(file_path, form):
    """
    Given an uploaded image, manipulats the image depending on the options
    provided from the form.

    :param file_path: Path to the saved image
    :param form: The submitted form with configuration options

    :return: (gif, images); where gif is the path to a created gif or the empty
    string if there is none, and images is a list of paths to resulting images
    """
    return '', []

def get_cli_arguments(form):
    """
    Given a submitted form with configuration options for the image
    manipulation, determines which command line arugments must be given to the
    script to achieve the configuration.

    :return: A list of arguments to be provided to the command line interface
    for the image manipulation script.
    """
    return ['--output', app.config['OUTPUT_FOLDER']]
