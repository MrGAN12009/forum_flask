"""WebSocket события для чата"""

from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room
from app import socketio, db
from app.models import ChatMessage, User
from app.utils import allowed_file, save_picture
import base64
import secrets
import os


@socketio.on('connect')
def handle_connect():
    """Подключение к WebSocket"""
    if current_user.is_authenticated:
        # Присоединяемся к персональной комнате пользователя
        join_room(f'user_{current_user.id}')
        emit('connected', {'user_id': current_user.id})
    else:
        return False  # Отклоняем подключение неавторизованных


@socketio.on('disconnect')
def handle_disconnect():
    """Отключение от WebSocket"""
    if current_user.is_authenticated:
        leave_room(f'user_{current_user.id}')


@socketio.on('join_chat')
def handle_join_chat(data):
    """Присоединение к чату с пользователем"""
    if not current_user.is_authenticated:
        return
    
    recipient_id = data.get('recipient_id')
    if not recipient_id:
        return
    
    # Создаем уникальную комнату для двух пользователей
    room = f'chat_{min(current_user.id, recipient_id)}_{max(current_user.id, recipient_id)}'
    join_room(room)
    
    emit('joined_chat', {
        'room': room,
        'user_id': current_user.id,
        'recipient_id': recipient_id
    })


@socketio.on('leave_chat')
def handle_leave_chat(data):
    """Покинуть чат"""
    if not current_user.is_authenticated:
        return
    
    recipient_id = data.get('recipient_id')
    if not recipient_id:
        return
    
    room = f'chat_{min(current_user.id, recipient_id)}_{max(current_user.id, recipient_id)}'
    leave_room(room)


@socketio.on('send_message')
def handle_send_message(data):
    """Отправка сообщения"""
    if not current_user.is_authenticated:
        return
    
    recipient_id = data.get('recipient_id')
    content = data.get('content', '').strip()
    image_data = data.get('image')  # Base64 encoded image
    
    if not recipient_id or not content:
        emit('error', {'message': 'Не указан получатель или текст сообщения'})
        return
    
    # Проверяем существование получателя
    recipient = User.query.get(recipient_id)
    if not recipient:
        emit('error', {'message': 'Пользователь не найден'})
        return
    
    # Обработка изображения если есть
    image_filename = None
    if image_data:
        try:
            # Декодируем base64
            image_bytes = base64.b64decode(image_data.split(',')[1])
            
            # Генерируем имя файла
            random_hex = secrets.token_hex(8)
            image_filename = f'{random_hex}.png'
            
            # Сохраняем файл
            from flask import current_app
            image_path = os.path.join(current_app.config['CHAT_FOLDER'], image_filename)
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
        except Exception as e:
            print(f'Error saving image: {e}')
    
    # Создаем сообщение в БД
    message = ChatMessage(
        content=content,
        image=image_filename,
        sender_id=current_user.id,
        recipient_id=recipient_id
    )
    
    db.session.add(message)
    db.session.commit()
    
    # Формируем данные сообщения
    message_data = message.to_dict()
    
    # Отправляем в комнату чата
    room = f'chat_{min(current_user.id, recipient_id)}_{max(current_user.id, recipient_id)}'
    emit('new_message', message_data, room=room)
    
    # Отправляем уведомление получателю
    emit('notification', {
        'type': 'new_message',
        'message': message_data
    }, room=f'user_{recipient_id}')


@socketio.on('typing')
def handle_typing(data):
    """Пользователь печатает"""
    if not current_user.is_authenticated:
        return
    
    recipient_id = data.get('recipient_id')
    if not recipient_id:
        return
    
    room = f'chat_{min(current_user.id, recipient_id)}_{max(current_user.id, recipient_id)}'
    emit('user_typing', {
        'user_id': current_user.id,
        'username': current_user.username
    }, room=room, include_self=False)


@socketio.on('mark_read')
def handle_mark_read(data):
    """Отметить сообщения как прочитанные"""
    if not current_user.is_authenticated:
        return
    
    sender_id = data.get('sender_id')
    if not sender_id:
        return
    
    # Помечаем все непрочитанные сообщения от отправителя как прочитанные
    messages = ChatMessage.query.filter_by(
        sender_id=sender_id,
        recipient_id=current_user.id,
        is_read=False
    ).all()
    
    for msg in messages:
        msg.is_read = True
    
    db.session.commit()
    
    emit('messages_marked_read', {
        'count': len(messages),
        'sender_id': sender_id
    })

