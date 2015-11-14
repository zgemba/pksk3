from flask import current_app
import os


def allowed_file(filename):
    return '.' in filename and \
           filename.lower().rsplit('.', 1)[1] in current_app.config["ALLOWED_EXTENSIONS"]


def make_unique_filename(filename):
    if not os.path.exists(filename):
        return filename
    version = 1
    path = os.path.split(filename)[0]
    while True:
        (name, ext) = os.path.splitext(os.path.basename(filename))
        new_file = os.path.join(path, name + str(version) + ext)
        if not os.path.exists(new_file):
            break
        version += 1
    # noinspection PyUnboundLocalVariable
    return new_file


