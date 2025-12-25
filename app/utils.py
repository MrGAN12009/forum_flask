"""Вспомогательные функции"""

import os
import secrets
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename
from flask_mail import Message
from app import mail
from threading import Thread


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


def send_async_email(app, msg):
    """Отправка email в отдельном потоке"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f'Error sending email: {e}')


def send_email(subject, recipient, text_body, html_body=None):
    """Отправка email сообщения"""
    msg = Message(subject,
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[recipient])
    msg.body = text_body
    if html_body:
        msg.html = html_body
    
    # Отправка в отдельном потоке, чтобы не блокировать основной процесс
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()


def send_verification_email(user):
    """Отправка кода подтверждения на email"""
    code = user.generate_verification_code()
    
    subject = 'Подтверждение email - ForumCodes'
    text_body = f'''Здравствуйте, {user.username}!

Ваш код подтверждения: {code}

Код действителен в течение 1 часа.

Если вы не регистрировались на ForumCodes, просто игнорируйте это письмо.

С уважением,
Команда ForumCodes
'''
    
    html_body = f'''
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <h2 style="color: #0D6EFD;">Подтверждение email</h2>
            <p>Здравствуйте, <strong>{user.username}</strong>!</p>
            <p>Ваш код подтверждения:</p>
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #0D6EFD; margin: 20px 0;">
                {code}
            </div>
            <p>Код действителен в течение <strong>1 часа</strong>.</p>
            <p>Если вы не регистрировались на ForumCodes, просто игнорируйте это письмо.</p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="color: #666; font-size: 12px;">
                С уважением,<br>
                Команда ForumCodes<br>
                <a href="https://forumcodes.online">forumcodes.online</a>
            </p>
        </div>
    </body>
    </html>
    '''
    
    send_email(subject, user.email, text_body, html_body)

