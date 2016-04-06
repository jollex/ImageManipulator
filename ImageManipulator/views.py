import os, subprocess, json, uuid, threading
from flask import render_template, send_from_directory, url_for, jsonify
from . import app, db
from .forms import ImageManipulationForm
from .models import Image

@app.route('/', methods=['GET', 'POST'])
def start():
    form = ImageManipulationForm()

    if form.validate_on_submit():
        old_filename = form.image.data.filename
        _, ext = os.path.splitext(old_filename)
        filename = str(uuid.uuid4()) + ext
        image = Image(old_filename, filename, '')
        db.session.add(image)
        db.session.commit()

        file_path = os.path.join(app.config['IMAGE_DIR'], filename)
        form.image.data.save(file_path)
        start_image_processing_and_update_files(file_path, form, image.id)

        return render_template('result.html', preview_filename=filename,
            old_filename=old_filename, image_id=image.id)

    return render_template('index.html', form=form)

@app.route('/_results/<image_id>', methods=['GET'])
def send_results(image_id):
    image = Image.query.filter_by(id=image_id).first()
    if image is not None and image.results:
        return jsonify(**json.loads(image.results))
    else:
        return ''

def start_image_processing_and_update_files(file_path, form, image_id):
    """
    This method starts the image manipulation method in the background.

    :param file_path: Argument to pass to manipulate_image, the path to the
    image to manipulate.
    :param form: Argument to pass to manipulate_image, the form with
    configuration options.
    :param image_id: The id of the Image in the DB.
    """
    thread = threading.Thread(target=manipulate_image,
        args=(file_path, form, image_id))
    thread.daemon = True
    thread.start()

def manipulate_image(file_path, form, image_id):
    """
    Manipulates the image at the given file_path depending on the options
    provided from the given form. Once the resulting gif/frames are returned by
    the script, the Image in the DB is updated.

    :param file_path: Path to the saved image
    :param form: The submitted form with configuration options
    :param image_id: The id of the Image in the DB
    """
    script_path = app.config['SCRIPT_PATH']
    output_dir = app.config['IMAGE_DIR']
    arguments = ['--output', output_dir] + get_cli_arguments(form)
    command = [app.config['PYTHON'], script_path, file_path] + arguments

    # the script outputs the following dictionary:
    # {"gif": "path_to.gif", "frames": ["path_to_frame.png", ...]}
    results = subprocess.check_output(command)

    image = Image.query.filter_by(id=image_id).first()
    if image is not None:
        image.results = results
        db.session.commit()

def get_cli_arguments(form):
    """
    Given a submitted form with configuration options for the image
    manipulation, determines which command line arugments must be given to the
    script to achieve the configuration.

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
