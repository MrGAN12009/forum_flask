"""Модели базы данных"""

from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
import secrets


class User(UserMixin, db.Model):
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), default='default-avatar.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Email verification fields
    email_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6), nullable=True)
    verification_code_expires = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    topics = db.relationship('Topic', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    sent_messages = db.relationship('ChatMessage', foreign_keys='ChatMessage.sender_id',
                                   backref='sender', lazy='dynamic', cascade='all, delete-orphan')
    received_messages = db.relationship('ChatMessage', foreign_keys='ChatMessage.recipient_id',
                                       backref='recipient', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Установить хеш пароля"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверить пароль"""
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_code(self):
        """Сгенерировать код подтверждения (6 цифр)"""
        self.verification_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        self.verification_code_expires = datetime.utcnow() + timedelta(hours=1)
        return self.verification_code
    
    def verify_code(self, code):
        """Проверить код подтверждения"""
        if not self.verification_code or not self.verification_code_expires:
            return False
        
        # Проверка истечения срока
        if datetime.utcnow() > self.verification_code_expires:
            return False
        
        # Проверка кода
        if self.verification_code == code:
            self.email_verified = True
            self.verification_code = None
            self.verification_code_expires = None
            return True
        
        return False
    
    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Загрузить пользователя по ID для Flask-Login"""
    return User.query.get(int(user_id))


class Topic(db.Model):
    """Модель топика форума"""
    __tablename__ = 'topics'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    views = db.Column(db.Integer, default=0)
    
    # Relationships
    posts = db.relationship('Post', backref='topic', lazy='dynamic', cascade='all, delete-orphan',
                          order_by='Post.created_at')
    
    def __repr__(self):
        return f'<Topic {self.title}>'
    
    @property
    def post_count(self):
        """Количество постов в топике"""
        return self.posts.count()


class Post(db.Model):
    """Модель поста (сообщения в топике)"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    
    def __repr__(self):
        return f'<Post {self.id} in Topic {self.topic_id}>'


class ChatMessage(db.Model):
    """Модель сообщения в чате"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_read = db.Column(db.Boolean, default=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<ChatMessage from {self.sender_id} to {self.recipient_id}>'
    
    def to_dict(self):
        """Преобразовать сообщение в словарь для JSON"""
        return {
            'id': self.id,
            'content': self.content,
            'image': self.image,
            'created_at': self.created_at.isoformat(),
            'is_read': self.is_read,
            'sender_id': self.sender_id,
            'sender_username': self.sender.username,
            'sender_avatar': self.sender.avatar,
            'recipient_id': self.recipient_id
        }

