import io

from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm,\
    CommentForm
from .. import db
from ..models import Permission, Role, User, Post, Comment, Tag
from ..decorators import admin_required, permission_required

import os
from flask import send_from_directory
from flask_ckeditor import upload_success, upload_fail

from werkzeug.exceptions import RequestEntityTooLarge
import uuid
from PIL import Image, ImageDraw, ImageFont


def add_copyright(response, filepath, fontpath, ext):
    photo = Image.open(response)
    # to save 'png' as 'jpeg'
    # photo = photo.convert('RGB')
    w, h = photo.size
    ratio = w / h
    copy_width = 15
    text = 'Blitzschnee'
    drawing = ImageDraw.Draw(photo)

    for font_size in range(w, 0, -1):
        font = ImageFont.truetype(fontpath, font_size)
        text_w, text_h = drawing.textsize(text, font)
        if (text_w <= w*copy_width/100) or (text_w <= 150):
            break

    copy_image = Image.new('RGBA', (text_w, text_h))
    copy_drawing = ImageDraw.Draw(copy_image)
    copy_drawing.text((0, 0), text, font=font)

    copy_w, copy_h = copy_image.size
    position = w - int(copy_w*1.2), h - int(copy_h*1.2)

    photo.paste(copy_image, position, copy_image.convert('RGBA'))

    file_format = 'JPEG' if ext.lower() == 'jpg' else ext.upper()
    photo.save(filepath, format=file_format, subsampling=0, quality='web_maximum')


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query.filter_by(status=Post.STATUS_PUBLIC)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts,
                           show_followed=show_followed, pagination=pagination,
                           active_main='active')


@main.route('/search', methods=['GET', 'POST'])
def search():
    page = request.args.get('page', 1, type=int)
    search = ''
    posts = []
    tags = []
    pagination = []
    if request.method == 'GET':
        if request.args.get('q'):
            search = request.args.get('q')
            title_checked = request.args.get('title')
            body_checked = request.args.get('body')
            if (title_checked and body_checked) or (not title_checked) and (not body_checked):
                mask = Post.body.contains(search) | Post.title.contains(search)
            elif title_checked:
                mask = Post.title.contains(search)
            elif body_checked:
                mask = Post.body.contains(search)
            query = Post.query.filter_by(status=Post.STATUS_PUBLIC).filter(mask)
            pagination = query.order_by(Post.timestamp.desc()).paginate(
                page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                error_out=False)
            posts = pagination.items
        elif request.args.get('t'):
            search = request.args.get('t')
            query = db.session.query(Tag).filter(Tag.name.like('%' + str(search) + '%'))
            pagination = query.order_by(Tag.name.desc()).paginate(
                page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                error_out=False)
            tags = pagination.items
    return render_template('search.html', posts=posts, tags=tags,
                           pagination=pagination, search=search)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Ваш комментарий успешно опубликован', 'alert_success')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data,
                    author=current_user._get_current_object(),
                    status=form.status.data,
                    tags=form.tags.data)
        db.session.add(post)
        db.session.commit()
        flash('Запись успешно создана', 'alert_success')
        return redirect(url_for('.post', id=post.id))
    return render_template('create.html', form=form, active_create='active')


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author:
        if not current_user.can(Permission.ADMIN):
            abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.status = form.status.data
        post.tags = form.tags.data
        post.refresh_timestamp_modified()
        db.session.add(post)
        db.session.commit()
        flash('Запись успешно отредактирована', 'alert_success')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.status.data = post.status
    form.tags.data = post.tags
    return render_template('edit_post.html', form=form, post=post)


@main.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    if request.method == 'POST':
        post.status = Post.STATUS_DELETED
        db.session.add(post)
        db.session.commit()
        flash('Запись успешно удалена', 'alert_success')
        return redirect(url_for('.index'))


@main.route('/recover/<int:id>', methods=['POST'])
@login_required
def recover(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    if request.method == 'POST':
        post.status = Post.STATUS_DRAFT
        db.session.add(post)
        db.session.commit()
        flash('Запись успешно восстановлена', 'alert_success')
        return redirect(url_for('.index'))


@main.route('/publish/<int:id>', methods=['POST'])
@login_required
def publish(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    if request.method == 'POST':
        post.status = Post.STATUS_PUBLIC
        post.refresh_timestamp()
        db.session.add(post)
        db.session.commit()
        flash('Запись успешно опубликована', 'alert_success')
        return redirect(url_for('.index'))


@main.route('/tags', methods=['GET', 'POST'])
def tags_index():
    page = request.args.get('page', 1, type=int)
    query = Tag.query
    pagination = query.order_by(Tag.name.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    tags = pagination.items
    return render_template('tags_index.html', tags=tags,
                           pagination=pagination, active_tags='active')


@main.route('/tags/<slug>', methods=['GET', 'POST'])
def tag_detail(slug):
    page = request.args.get('page', 1, type=int)
    tag = Tag.query.filter(Tag.slug == slug).first_or_404()
    query = tag.posts
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('tag_detail.html', tag=tag, posts=posts,
                           pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    active_profile = ''
    if user == current_user:
        active_profile = 'active'
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination, active_profile=active_profile)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Ваш профиль успешно обновлен', 'alert_success')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('Профиль пользователя успешно обновлен', 'alert_success')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Несуществующий пользователь', 'alert_error')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('Вы уже подписаны на этого пользователя!', 'alert_error')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('Вы теперь подписаны на %s' % username, 'alert_success')
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Несуществующий пользователь', 'alert_error')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('Вы не подписаны на этого пользователя', 'alert_error')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('Вы больше не подписаны на %s' % username, 'alert_success')
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Несуществующий пользователь', 'alert_error')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Несуществующий пользователь', 'alert_error')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.status = comment.STATUS_PUBLIC
    db.session.add(comment)
    db.session.commit()
    flash('Комментарий восстановлен', 'alert_success')
    return redirect(url_for('.post', id=comment.post.id))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.status = comment.STATUS_DISABLED_BY_MODERATOR
    db.session.add(comment)
    db.session.commit()
    flash('Комментарий скрыт', 'alert_success')
    return redirect(url_for('.post', id=comment.post.id))


@main.route('/moderate/enable_user/<int:id>')
@login_required
def moderate_enable_user(id):
    comment = Comment.query.get_or_404(id)
    if current_user != comment.author:
        abort(403)
    comment.status = comment.STATUS_PUBLIC
    db.session.add(comment)
    db.session.commit()
    flash('Комментарий восстановлен', 'alert_success')
    return redirect(url_for('.post',
                            id=comment.post_id))


@main.route('/moderate/disable_user/<int:id>')
@login_required
def moderate_disable_user(id):
    comment = Comment.query.get_or_404(id)
    if current_user != comment.author:
        abort(403)
    comment.status = comment.STATUS_DELETED_BY_USER
    db.session.add(comment)
    db.session.commit()
    flash('Комментарий скрыт', 'alert_success')
    return redirect(url_for('.post',
                            id=comment.post_id))


@main.route('/files/<path:filename>')
def uploaded_files(filename):
    app = current_app._get_current_object()
    path = app.config['UPLOADED_PATH_IMAGES']
    return send_from_directory(path, filename)


@main.route('/upload', methods=['POST'])
def upload():
    app = current_app._get_current_object()

    try:
        f = request.files.get('upload')
    except RequestEntityTooLarge:
        return upload_fail(message='Размер файла слишком большой!')

    extension = f.filename.split('.')[-1].lower()
    # make unique filename
    f.filename = f.filename.split('.')[0] + '_' + uuid.uuid4().hex[:8] + '.' + f.filename.split('.')[-1]

    filepath = os.path.join(app.config['UPLOADED_PATH_IMAGES']) + f.filename
    fontpath = os.path.abspath(os.path.join(app.config['STATIC_DIR']) + '/fonts')
    fontpath = fontpath + '/' + os.listdir(fontpath)[0]

    add_copyright(f, filepath, fontpath, extension)

    url = url_for('main.uploaded_files', filename=f.filename)
    return jsonify(url=url)


@main.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('autocomplete')
    query = db.session.query(Tag.name).\
        filter(Tag.name.like('%' + str(search.split(',')[-1].strip()) + '%'))
    results = [i[0] for i in query.all()]
    return jsonify(json_list=results)


@main.route('/mention', methods=['GET'])
def mention():
    search = request.args.get('mentionString')
    query = db.session.query(User.username) \
        .filter(User.username.like('%' + str(search) + '%'))
    results = [
        {'id': name, 'username': name[1:]} for name in ['@' + i[0] for i in query.all()]
    ]
    return {'result': results}
