#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных с тестовыми данными
"""

import os
import sys

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Topic, Post

def init_db():
    """Инициализация БД с тестовыми данными"""
    app = create_app('development')
    
    with app.app_context():
        print('Создание тестовых пользователей...')
        
        # Проверяем, есть ли уже пользователи
        if User.query.count() > 0:
            print('База данных уже содержит данные. Пропускаем инициализацию.')
            return
        
        # Создаем тестовых пользователей
        users = []
        for i in range(1, 4):
            user = User(
                username=f'user{i}',
                email=f'user{i}@example.com'
            )
            user.set_password('password123')
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        print(f'✓ Создано {len(users)} тестовых пользователей')
        
        # Создаем тестовые топики
        print('Создание тестовых топиков...')
        
        topics_data = [
            {
                'title': 'Добро пожаловать на форум!',
                'content': 'Это первый тестовый топик. Здесь вы можете обсуждать любые темы и общаться с другими пользователями.',
                'author': users[0]
            },
            {
                'title': 'Как пользоваться форумом?',
                'content': 'В этом топике мы расскажем о возможностях нашего форума. Вы можете создавать топики, отвечать на сообщения и общаться в чате.',
                'author': users[1]
            },
            {
                'title': 'Предложения и идеи',
                'content': 'Есть идеи по улучшению форума? Делитесь ими здесь!',
                'author': users[2]
            }
        ]
        
        topics = []
        for topic_data in topics_data:
            topic = Topic(
                title=topic_data['title'],
                content=topic_data['content'],
                author=topic_data['author']
            )
            topics.append(topic)
            db.session.add(topic)
        
        db.session.commit()
        print(f'✓ Создано {len(topics)} тестовых топиков')
        
        # Создаем тестовые посты
        print('Создание тестовых постов...')
        
        posts_data = [
            {
                'content': 'Спасибо за приветствие! Рад быть здесь.',
                'topic': topics[0],
                'author': users[1]
            },
            {
                'content': 'Отличный форум! Очень удобный интерфейс.',
                'topic': topics[0],
                'author': users[2]
            },
            {
                'content': 'Можно загружать изображения в сообщениях?',
                'topic': topics[1],
                'author': users[0]
            },
            {
                'content': 'Да, при создании поста есть возможность загрузить изображение!',
                'topic': topics[1],
                'author': users[1]
            }
        ]
        
        for post_data in posts_data:
            post = Post(
                content=post_data['content'],
                topic=post_data['topic'],
                author=post_data['author']
            )
            db.session.add(post)
        
        db.session.commit()
        print(f'✓ Создано {len(posts_data)} тестовых постов')
        
        print('\n=== Инициализация завершена ===')
        print('Тестовые пользователи:')
        for user in users:
            print(f'  - {user.username} / {user.email} / пароль: password123')
        print('\nТеперь вы можете войти на форум используя эти данные.')

if __name__ == '__main__':
    init_db()

