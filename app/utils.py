"""Вспомогательные функции"""

import os
import secrets
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename):
    """Проверка разрешенного расширения файла"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_picture(form_picture, folder, size=None):
    """
    Сохранение изображения
    
    Args:
        form_picture: файл из формы
        folder: папка для сохранения (относительно UPLOAD_FOLDER)
        size: кортеж (width, height) для изменения размера, или None
    
    Returns:
        имя сохраненного файла
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    
    # Полный путь к файлу
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder, picture_fn)
    
    # Изменение размера если указан
    if size:
        img = Image.open(form_picture)
        img.thumbnail(size)
        img.save(picture_path)
    else:
        form_picture.save(picture_path)
    
    return picture_fn


def delete_picture(filename, folder):
    """
    Удаление изображения
    
    Args:
        filename: имя файла
        folder: папка (относительно UPLOAD_FOLDER)
    """
    if filename and filename != 'default-avatar.png':
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

