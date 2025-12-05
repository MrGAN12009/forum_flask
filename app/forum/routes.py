"""Маршруты форума"""

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.forum import forum_bp
from app import db
from app.models import Topic, Post
from app.utils import allowed_file, save_picture


@forum_bp.route('/')
def index():
    """Список всех топиков"""
    page = request.args.get('page', 1, type=int)
    
    topics = Topic.query.order_by(Topic.updated_at.desc()).paginate(
        page=page,
        per_page=current_app.config['TOPICS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('forum/index.html', topics=topics)


@forum_bp.route('/topic/<int:topic_id>')
def topic_view(topic_id):
    """Просмотр конкретного топика"""
    topic = Topic.query.get_or_404(topic_id)
    
    # Увеличиваем счетчик просмотров
    topic.views += 1
    db.session.commit()
    
    page = request.args.get('page', 1, type=int)
    
    posts = Post.query.filter_by(topic_id=topic_id).order_by(Post.created_at.asc()).paginate(
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('forum/topic.html', topic=topic, posts=posts)


@forum_bp.route('/topic/create', methods=['GET', 'POST'])
@login_required
def topic_create():
    """Создание нового топика"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if not title or len(title) < 5:
            flash('Заголовок должен содержать минимум 5 символов', 'danger')
            return render_template('forum/topic_create.html')
        
        if not content or len(content) < 10:
            flash('Содержание должно содержать минимум 10 символов', 'danger')
            return render_template('forum/topic_create.html')
        
        topic = Topic(
            title=title,
            content=content,
            author_id=current_user.id
        )
        
        db.session.add(topic)
        db.session.commit()
        
        flash('Топик успешно создан!', 'success')
        return redirect(url_for('forum.topic_view', topic_id=topic.id))
    
    return render_template('forum/topic_create.html')


@forum_bp.route('/topic/<int:topic_id>/post', methods=['POST'])
@login_required
def post_create(topic_id):
    """Создание нового поста в топике"""
    topic = Topic.query.get_or_404(topic_id)
    
    content = request.form.get('content', '').strip()
    
    if not content or len(content) < 1:
        flash('Сообщение не может быть пустым', 'danger')
        return redirect(url_for('forum.topic_view', topic_id=topic_id))
    
    # Обработка изображения
    image_filename = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            image_filename = save_picture(file, 'posts')
    
    post = Post(
        content=content,
        image=image_filename,
        author_id=current_user.id,
        topic_id=topic_id
    )
    
    db.session.add(post)
    
    # Обновляем время обновления топика
    topic.updated_at = db.func.now()
    
    db.session.commit()
    
    flash('Сообщение успешно добавлено!', 'success')
    return redirect(url_for('forum.topic_view', topic_id=topic_id))


@forum_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def post_delete(post_id):
    """Удаление поста"""
    post = Post.query.get_or_404(post_id)
    
    # Проверка прав
    if post.author_id != current_user.id:
        flash('У вас нет прав на удаление этого сообщения', 'danger')
        return redirect(url_for('forum.topic_view', topic_id=post.topic_id))
    
    topic_id = post.topic_id
    
    # Удаление изображения если есть
    if post.image:
        from app.utils import delete_picture
        delete_picture(post.image, 'posts')
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Сообщение удалено', 'info')
    return redirect(url_for('forum.topic_view', topic_id=topic_id))

