"""Маршруты профиля пользователя"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.profile import profile_bp
from app import db
from app.models import User, Topic, Post
from app.utils import allowed_file, save_picture, delete_picture


@profile_bp.route('/<int:user_id>')
def view(user_id):
    """Просмотр профиля пользователя"""
    user = User.query.get_or_404(user_id)
    
    # Получаем статистику
    topics_count = user.topics.count()
    posts_count = user.posts.count()
    
    # Последние топики пользователя
    recent_topics = user.topics.order_by(Topic.created_at.desc()).limit(5).all()
    
    # Последние посты пользователя
    recent_posts = user.posts.order_by(Post.created_at.desc()).limit(5).all()
    
    return render_template('profile/view.html',
                         user=user,
                         topics_count=topics_count,
                         posts_count=posts_count,
                         recent_topics=recent_topics,
                         recent_posts=recent_posts)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Редактирование профиля"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        
        # Валидация
        if not username or len(username) < 3:
            flash('Имя пользователя должно содержать минимум 3 символа', 'danger')
            return render_template('profile/edit.html')
        
        # Проверка уникальности имени (если изменилось)
        if username != current_user.username:
            if User.query.filter_by(username=username).first():
                flash('Это имя пользователя уже занято', 'danger')
                return render_template('profile/edit.html')
            
            current_user.username = username
        
        # Обработка аватара
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename and allowed_file(file.filename):
                # Удаляем старый аватар
                if current_user.avatar != 'default-avatar.png':
                    delete_picture(current_user.avatar, 'avatars')
                
                # Сохраняем новый с изменением размера
                avatar_filename = save_picture(file, 'avatars', size=(200, 200))
                current_user.avatar = avatar_filename
        
        db.session.commit()
        flash('Профиль обновлен!', 'success')
        return redirect(url_for('profile.view', user_id=current_user.id))
    
    return render_template('profile/edit.html')


@profile_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Изменение пароля"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Валидация
        if not current_user.check_password(current_password):
            flash('Неверный текущий пароль', 'danger')
            return render_template('profile/change_password.html')
        
        if len(new_password) < 6:
            flash('Новый пароль должен содержать минимум 6 символов', 'danger')
            return render_template('profile/change_password.html')
        
        if new_password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            return render_template('profile/change_password.html')
        
        # Обновляем пароль
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Пароль успешно изменен!', 'success')
        return redirect(url_for('profile.view', user_id=current_user.id))
    
    return render_template('profile/change_password.html')

