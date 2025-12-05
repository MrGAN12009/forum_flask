"""Маршруты чата"""

from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.chat import chat_bp
from app import db
from app.models import User, ChatMessage
from sqlalchemy import or_, and_


@chat_bp.route('/')
@login_required
def index():
    """Главная страница чата"""
    # Получаем список пользователей с которыми есть переписка
    users_with_messages = db.session.query(User).join(
        ChatMessage,
        or_(
            and_(ChatMessage.sender_id == User.id, ChatMessage.recipient_id == current_user.id),
            and_(ChatMessage.recipient_id == User.id, ChatMessage.sender_id == current_user.id)
        )
    ).filter(User.id != current_user.id).distinct().all()
    
    # Получаем всех пользователей для возможности начать новый чат
    all_users = User.query.filter(User.id != current_user.id).all()
    
    return render_template('chat/index.html', 
                         users_with_messages=users_with_messages,
                         all_users=all_users)


@chat_bp.route('/user/<int:user_id>')
@login_required
def chat_with_user(user_id):
    """Чат с конкретным пользователем"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Нельзя отправить сообщение самому себе'}), 400
    
    # Получаем историю сообщений
    messages = ChatMessage.query.filter(
        or_(
            and_(ChatMessage.sender_id == current_user.id, ChatMessage.recipient_id == user_id),
            and_(ChatMessage.sender_id == user_id, ChatMessage.recipient_id == current_user.id)
        )
    ).order_by(ChatMessage.created_at.asc()).all()
    
    # Помечаем непрочитанные сообщения как прочитанные
    unread_messages = ChatMessage.query.filter_by(
        sender_id=user_id,
        recipient_id=current_user.id,
        is_read=False
    ).all()
    
    for msg in unread_messages:
        msg.is_read = True
    
    db.session.commit()
    
    return render_template('chat/conversation.html', 
                         recipient=user,
                         messages=messages)


@chat_bp.route('/messages/<int:user_id>')
@login_required
def get_messages(user_id):
    """API для получения сообщений с пользователем"""
    messages = ChatMessage.query.filter(
        or_(
            and_(ChatMessage.sender_id == current_user.id, ChatMessage.recipient_id == user_id),
            and_(ChatMessage.sender_id == user_id, ChatMessage.recipient_id == current_user.id)
        )
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return jsonify([msg.to_dict() for msg in messages])


@chat_bp.route('/unread-count')
@login_required
def unread_count():
    """Количество непрочитанных сообщений"""
    count = ChatMessage.query.filter_by(
        recipient_id=current_user.id,
        is_read=False
    ).count()
    
    return jsonify({'count': count})

