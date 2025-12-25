"""Маршруты аутентификации"""

from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import auth_bp
from app import db
from app.models import User
from app.utils import send_verification_email


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового пользователя"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Валидация
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Имя пользователя должно содержать минимум 3 символа')
        
        if not email or '@' not in email:
            errors.append('Введите корректный email')
        
        if not password or len(password) < 6:
            errors.append('Пароль должен содержать минимум 6 символов')
        
        if password != confirm_password:
            errors.append('Пароли не совпадают')
        
        # Проверка уникальности
        if User.query.filter_by(username=username).first():
            errors.append('Это имя пользователя уже занято')
        
        if User.query.filter_by(email=email).first():
            errors.append('Этот email уже зарегистрирован')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')
        
        # Создание пользователя
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Отправка кода подтверждения
        send_verification_email(user)
        db.session.commit()  # Сохраняем код в БД
        
        # Сохраняем user_id в сессии для проверки
        session['pending_verification_user_id'] = user.id
        
        flash('Регистрация успешна! Проверьте вашу почту и введите код подтверждения.', 'success')
        return redirect(url_for('auth.verify_email'))
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Вход пользователя"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False) == 'on'
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Проверка подтверждения email
            if not user.email_verified:
                flash('Пожалуйста, подтвердите ваш email перед входом.', 'warning')
                send_verification_email(user)
                db.session.commit()
                session['pending_verification_user_id'] = user.id
                return redirect(url_for('auth.verify_email'))
            
            login_user(user, remember=remember)
            flash('Вы успешно вошли в систему!', 'success')
            
            # Перенаправление на следующую страницу или главную
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Неверный email или пароль', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Выход пользователя"""
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    """Подтверждение email адреса"""
    # Проверяем, есть ли user_id в сессии
    user_id = session.get('pending_verification_user_id')
    if not user_id:
        flash('Сначала зарегистрируйтесь', 'warning')
        return redirect(url_for('auth.register'))
    
    user = User.query.get(user_id)
    if not user:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('auth.register'))
    
    # Если уже подтвержден
    if user.email_verified:
        session.pop('pending_verification_user_id', None)
        flash('Email уже подтвержден', 'info')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        
        if not code:
            flash('Введите код подтверждения', 'danger')
            return render_template('auth/verify_email.html', email=user.email)
        
        if user.verify_code(code):
            db.session.commit()
            session.pop('pending_verification_user_id', None)
            flash('Email успешно подтвержден! Теперь вы можете войти.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Неверный или истёкший код подтверждения', 'danger')
    
    return render_template('auth/verify_email.html', email=user.email)


@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Повторная отправка кода подтверждения"""
    user_id = session.get('pending_verification_user_id')
    if not user_id:
        flash('Сначала зарегистрируйтесь', 'warning')
        return redirect(url_for('auth.register'))
    
    user = User.query.get(user_id)
    if not user:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('auth.register'))
    
    if user.email_verified:
        session.pop('pending_verification_user_id', None)
        flash('Email уже подтвержден', 'info')
        return redirect(url_for('auth.login'))
    
    send_verification_email(user)
    db.session.commit()
    flash('Новый код отправлен на вашу почту', 'success')
    return redirect(url_for('auth.verify_email'))

