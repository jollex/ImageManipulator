import os, subprocess, json, uuid
from flask import render_template, send_from_directory
from app import app
from .forms import ImageManipulationForm

ROOT_DIR = os.path.dirname(__file__)

@app.route('/', methods=['GET', 'POST'])
def start():
    form = ImageManipulationForm()

    if form.validate_on_submit():
        _, ext = os.path.splitext(form.image.data.filename)
        filename = str(uuid.uuid4()) + ext
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        form.image.data.save(file_path)

        gif, images = manipulate_image(file_path, form)
        return render_template('result.html', gif=gif, images=images)

    return render_template('index.html', form=form)

@app.route('/output/<path:filename>')
def send_file(filename):
    return send_from_directory(os.path.join(ROOT_DIR,
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
    script_path = app.config['SCRIPT_PATH']
    output_dir = os.path.join(ROOT_DIR, app.config['OUTPUT_FOLDER'])
    arguments = ['--output', output_dir] + get_cli_arguments(form)
    command = ['python', script_path, file_path] + arguments

    # the script outputs the following two lines:
    # "path_to.gif" or ""
    # ["path_to_frame.png", ...]
    result = subprocess.check_output(command)
    result = result.strip().split('\n')
    return map(json.loads, result)

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

    if form.animation.data in ['auto', 'custom']:
        if form.save_frames:
            arguments += ['--frames']

    if form.box_shape.data == 'vertical':
        arguments += ['--vertical']
    elif form.box_shape.data == 'horizontal':
        arguments += ['--horizontal']

    if not form.average.data:
        if form.rotation.data == 'flip':
            arguments += ['--flip']
        elif form.rotation.data == 'ninety':
            arguments += ['--ninety']

    if form.randomize.data:
        arguments += ['--random']
    if form.average.data:
        arguments += ['--average']

    return arguments
