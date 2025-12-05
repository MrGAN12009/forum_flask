#!/usr/bin/env python3
"""
Скрипт для создания дефолтного аватара
Запустите перед первым запуском Docker: python create_default_avatar.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_default_avatar():
    """Создает дефолтный аватар"""
    # Создаем изображение
    img = Image.new('RGB', (200, 200), color='#0D6EFD')
    draw = ImageDraw.Draw(img)
    
    # Рисуем круг (силуэт пользователя)
    # Голова
    draw.ellipse([60, 40, 140, 120], fill='white')
    # Тело
    draw.ellipse([40, 110, 160, 220], fill='white')
    
    # Сохраняем
    output_path = 'app/static/uploads/avatars/default-avatar.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f'✓ Дефолтный аватар создан: {output_path}')

if __name__ == '__main__':
    try:
        create_default_avatar()
    except Exception as e:
        print(f'Ошибка при создании аватара: {e}')
        print('Пожалуйста, создайте default-avatar.png вручную в app/static/uploads/avatars/')

