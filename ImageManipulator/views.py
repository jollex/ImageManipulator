import os, sys, subprocess, json, uuid, threading
from flask import render_template, send_from_directory, url_for, jsonify, request
from __init__ import app
from .forms import ImageManipulationForm

files = {}

@app.route('/', methods=['GET', 'POST'])
def start():
    form = ImageManipulationForm()

    if form.validate_on_submit():
        _, ext = os.path.splitext(form.image.data.filename)
        filename = str(uuid.uuid4()) + ext
        files[filename] = False
        file_path = os.path.join(app.config['STATIC_DIR'], filename)
        form.image.data.save(file_path)

        start_image_processing_and_update_files(file_path, form, filename)
        return render_template('result.html', preview_path=filename)

    return render_template('index.html', form=form)

@app.route('/_results/<path:filename>', methods=['GET'])
def send_results(filename):
    if filename in files and files[filename]:
        return jsonify(**files[filename])
    else:
        return ''

def start_image_processing_and_update_files(file_path, form, filename):
    """
    This method starts the image manipulation method in the background. It also
    passes along a callback to the method, which updates the files dict once
    the resulting images have been created.

    :param file_path: Argument to pass to manipulate_image, the path to the
    image to manipulate.
    :param form: Argument to pass to manipulate_image, the form with
    configuration options.
    :param filename: The base name of the image to manipulate, used as a key.
    """
    thread = threading.Thread(target=manipulate_image,
        args=(file_path, form, filename))
    thread.daemon = True
    thread.start()

def manipulate_image(file_path, form, filename):
    """
    Given an uploaded image, manipulats the image depending on the options
    provided from the form.

    :param file_path: Path to the saved image
    :param form: The submitted form with configuration options
    :param filename: The base name of the image to manipulate, used as a key.
    """
    script_path = app.config['SCRIPT_PATH']
    output_dir = app.config['STATIC_DIR']
    arguments = ['--output', output_dir] + get_cli_arguments(form)
    command = [app.config['PYTHON'], script_path, file_path] + arguments

    # the script outputs the following two lines:
    # "path_to.gif" or ""
    # ["path_to_frame.png", ...]
    result = subprocess.check_output(command)
    files[filename] = json.loads(result)

def get_cli_arguments(form):
    """
    Given a submitted form with configuration options for the image
    manipulation, determines which command line arugments must be given to the
    script to achieve the configuration.

    Animation options:
    Auto | One Frame | Custom
    Box size text field
    Number of frames text field
    Save frames checkbox
    If One Frame is selected, show box size text field
    If Custom is selected, show box size and number of frames sliders
    If Auto or Custom are selected, show save frames checkbox

    Box shape options:
    Square | Vertical | Horizontal

    Effects:
    Rotation drop down menu: [None, Flip, Ninety]; doesn't show
    Ninety if vertical or horizontal are selected.
    Randomize boxes checkbox
    Average boxes checkbox

    :param form: The ImageManipulationForm submitted by the user.

    :return: A list of arguments to be provided to the command line interface
    for the image manipulation script.
    """
    arguments = []

    if form.animation.data == 'auto':
        arguments += ['--auto']
    if form.animation.data == 'one_frame':
        arguments += ['--box_size', form.box_size.data]
    elif form.animation.data == 'custom':
        arguments += ['--box_size', form.box_size.data]
        arguments += ['--iterations', form.frames.data]

    if form.animation.data in ['auto', 'custom'] and form.save_frames.data:
        arguments += ['--frames']

    if form.box_shape.data == 'vertical':
        arguments += ['--vertical']
    elif form.box_shape.data == 'horizontal':
        arguments += ['--horizontal']

    if not form.average.data:
        if form.rotation.data == 'flip':
            arguments += ['--flip']
        elif form.rotation.data == 'ninety' and form.box_shape.data == 'square':
            arguments += ['--ninety']

    if form.randomize.data:
        arguments += ['--random']
    if form.average.data:
        arguments += ['--average']

    return arguments
