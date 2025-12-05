"""Главные маршруты приложения"""

from flask import render_template
from app.main import main_bp
from app.models import Topic, User
from app import db


@main_bp.route('/')
def index():
    """Главная страница"""
    # Последние топики
    recent_topics = Topic.query.order_by(Topic.created_at.desc()).limit(5).all()
    
    # Статистика
    stats = {
        'total_users': User.query.count(),
        'total_topics': Topic.query.count(),
    }
    
    return render_template('index.html', recent_topics=recent_topics, stats=stats)


@main_bp.route('/about')
def about():
    """Страница о проекте"""
    return render_template('about.html')

