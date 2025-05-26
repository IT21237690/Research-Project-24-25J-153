from flask import Blueprint, send_from_directory, current_app, abort
import os

images_bp = Blueprint('images', __name__)


@images_bp.route('/<filename>')
def serve_image(filename):
    """Serve images from the generated folder"""
    generated_folder = os.path.join('assets', 'generated')
    if not os.path.exists(os.path.join(generated_folder, filename)):
        abort(404)

    return send_from_directory(generated_folder, filename)