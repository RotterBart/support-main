from app import app, db, socketio
from flask import (
    Response, render_template, flash, redirect, url_for,
    request, send_from_directory, session,
    jsonify, send_file, current_app)
from app.forms import *
from app.email import send_password_reset_email
from flask_login import current_user, login_user, logout_user, login_required
from app.models import (Post, Report, User, Task)
from werkzeug.urls import url_parse
from datetime import datetime
from flask_socketio import emit, join_room, leave_room
from werkzeug.utils import secure_filename
import os
import re
import uuid
import xml.etree.ElementTree as ET

from app.customquery import CustomQuery
from app.servers import *
# from app.queue import Connection209
from datetime import datetime
from datetime import timedelta
from flask_socketio import SocketIO, emit, join_room, disconnect
from sqlalchemy_searchable import search
import psycopg2
from config import Config

thread = None


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)

    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POST_PER_PAGE'], False)
    next_url = url_for(
        'explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for(
        'explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html',
                           title='Explore',
                           posts=posts.items, 
                           next_url=next_url,
                           prev_url=prev_url)


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    unexecuted = len(Task.query.filter_by(
        task_executed=False,
        task_deleted=False,
        task_executor=current_user.id).all())

    tasks = Task.query.filter_by(task_deleted=False).order_by(
        Task.task_executed.asc()).order_by(
        Task.task_timestamp.desc()).all()
    form = AddTask()
    users = User.query.all()
    if form.validate_on_submit():
        app.logger.info('task submitted')

        task = Task(task_name=form.task_name.data,
                    task_description=form.task_description.data,
                    task_limitdate=form.task_limitdate.data.strftime(
                        '%d-%m-%Y'),
                    task_executor=form.task_executor.data.id)
        db.session.add(task)
        db.session.commit()
        flash('збс! Задача: ' + str(task.task_name), 'success')
        if current_user.is_admin:
            return redirect(url_for('home'))

    return render_template('home.html',
                           tasks=tasks,
                           form=form,
                           users=users,
                           unexecuted=unexecuted
                           )


@app.route('/execute/<task_id>', methods=['GET', 'POST'])
@login_required
def execute(task_id):
    task = Task.query.filter_by(task_id=task_id).first()
    action = request.args.get('action')
    if action == 'execute':
        task.task_executed = True
        task.task_executed_timestamp = datetime.now()
        db.session.commit()
        flash('Задача исполнена', 'success')
    elif action == 'delete':
        task.task_deleted = True
        db.session.commit()
        flash('Помечена удаленной', 'info')
    elif action == 'restore':
        task.task_deleted = False
        db.session.commit()
        flash('Восстановлено', 'info')
    elif action == 'edit':
        return redirect(url_for('edit_task', task_id=task.task_id))

    return redirect(url_for('home'))


@app.route('/edit_task/<task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.filter_by(task_id=task_id).first_or_404()
    form = TaskEditForm()
    if form.submit.data:
        task.task_name = form.task_name.data
        task.task_description = form.task_description.data
        task.task_execution_description = form.task_execution_description.data
        task.task_executor = form.task_executor.data.id
        task.task_limitdate = form.task_limitdate.data
        db.session.commit()
        flash('ЗБС', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.task_name.data = task.task_name
        form.task_description.data = task.task_description
        form.task_execution_description.data = task.task_execution_description
        form.task_executor.data.id = task.task_executor
        form.task_limitdate.data = task.task_limitdate
    return render_template('edit_task.html', form=form)


@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POST_PER_PAGE'], False)
    next_url = url_for(
        'index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.has_prev else None
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Posted!', 'success')
        return redirect(url_for('index'))
    return render_template('index.html',
                           title='Integrist',
                           posts=posts.items,
                           form=form,
                           next_url=next_url,
                           prev_url=prev_url
                           )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('vision'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'warning')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('vision')
        return redirect(next_page)
    return render_template('login.html', title='Login',
                           form=form)


@socketio.on('my event', namespace='/dn')
def my_event(msg):
    print(msg['data'])


@socketio.on('connect', namespace='/dn')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/dn')
def test_disconnect():
    print('Client disconnected')

# def background_stuff():
#     while True:
#         time.sleep(1)
#         t = str(datetime.now())
#         socketio.emit('message',
#                        {'data': 'This is data', 'time': t}, namespace='/dn')


@app.route('/dn', methods=['GET', 'POST'])
def dn():
    ###
    # global thread
    # if thread is None:
    #    thread = Thread(target=background_stuff)
    #    app.logger.info('THREAD STARTED')
    #    thread.start()
    ###
    history = DnString.query.order_by(DnString.rec_date.desc()).limit(10).all()
    text = 'Результат'
    form = DnTransform()
    if form.validate_on_submit():
        # text = str(
        #     form.dnForm.data.replace(' = ', '=').replace('\n', ', ')
        #     ).replace(' , ', ', ').replace('\r', '').replace(';', ', ')
        text = form.dnForm.data.split('\n')
        print( len(text))
        
        text.reverse()
        text = ','.join(text).replace('Phone = ', '2.5.4.20=\\').replace(
            ' = ', '=').replace(' , ', ',').replace('\r', '').replace(';', ', ')

        dnstring = DnString(dnstring=text, user_id=current_user.id)
        db.session.add(dnstring)
        db.session.commit()
        history = DnString.query.order_by(
            DnString.rec_date.desc()).limit(10).all()

        with pg.connect(
                host='10.10.2.209',
                dbname='DN_Container',
                user='postgres',
                password='Abu pfgjvybim'
            ) as conn:
            with conn.cursor() as cursor:
                newid = uuid.uuid4()
                cursor.execute(f"""INSERT INTO "public"."dnstring"("id", "dnstring", "rec_date", "timecreate", "active") VALUES ('{newid}', '{text}', '{datetime.now()}', '{datetime.now().date()}', 't');""")
                conn.commit()
        return render_template(
            'dn.html',
            form=form,
            text=text,
            history=history, counter=get_counter())
        
    return render_template('dn.html', form=form, text=text, history=history, counter=get_counter())


@app.route('/', methods=['GET', 'POST'])
@app.route('/vision', methods=['GET', 'POST'])
@login_required
def vision():
    contacts = Contact.query.all()
    current_time = datetime.now() + timedelta(minutes=4)
    contact_form = ServerContactsForm()
    SL = Connection218(current_user.region).get_server_list()
    return render_template(
        'vision.html',
        SL=SL,
        current_time=current_time,
        form=contact_form,
        contacts=contacts,
        counter=get_counter())

@app.route('/test_vision', methods=['GET', 'POST'])
@login_required
def test_vision():
    contacts = Contact.query.all()
    SL = Connection218(current_user.region).get_server_list()

    return render_template(
        'vision2.html',
        SL=SL,
        contacts=contacts)

@app.route('/serverinfo/<enterprise>', methods=['GET', 'POST'])
@login_required
def serverinfo(enterprise):
    form = ServerContactsForm()
    contact = Contact.query.filter_by(c_enterprise_id=enterprise).first()
    if form.validate_on_submit():
        contact.c_string = form.contact_string.data
        contact.c_description = form.desc.data
        contact.recdate = datetime.now()
        contact.workplacecount = form.workPlaceCount.data
        contact.password = form.password.data
        db.session.commit()
        flash('ЗБС сохранено {}'.format(enterprise), 'success')
        return redirect(url_for('serverinfo', enterprise=enterprise))
    elif request.method == 'GET':
        form.enterprise.data = contact.c_enterprise_id
        form.contact_string.data = contact.c_string
        form.desc.data = contact.c_description
        form.workPlaceCount.data = contact.workplacecount
        form.password.data = contact.password
    return render_template('serverinfo.html', contact=contact, form=form)


@app.route('/add_serverhistory/<enterprise>', methods=['GET', 'POST'])
@login_required
def add_serverhistory(enterprise):
    form = ServerContactsHistoryForm()
    ch = ContactHistory.query.filter_by(enterprise_id=enterprise).order_by(
        ContactHistory.rec_date.desc()).limit(10).all()

    if form.validate_on_submit():
        new_ch = ContactHistory(
            enterprise_id=enterprise,
            event=form.event.data,
            rec_date=datetime.now(),
            user_id=current_user.id)
        db.session.add(new_ch)
        db.session.commit()
        form.event.data = ''
        return redirect(url_for('vision', search=enterprise))
    return render_template('add_serverhistory.html', form=form, ch=ch, enterprise=enterprise)

def get_counter():
    with pg.connect(
        host='10.10.2.209',
        dbname='DN_Container',
        user='postgres',
        password='Abu pfgjvybim'
    ) as obl:
        with obl.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM dnstring WHERE active = True")
            count = cursor.fetchone()
            print(count)
            return count[0]


@app.route('/cc', methods=['GET', 'POST'])
@login_required
def cc():
    data = CompendiumItem.query.all()
    form = AddContact()
    form2 = AddDepartment()
    if form.validate_on_submit():
        ci = CompendiumItem(
            dep_id=form.department.data.dep_id,
            name=form.name.data,
            phone=form.phone.data,
            desc=form.desc.data)
        db.session.add(ci)
        db.session.commit()
        return redirect(url_for('cc'))
    elif form2.validate_on_submit():
        dep = Department(name=form2.dept.data)
        db.session.add(dep)
        db.session.commit()
        return redirect(url_for('cc'))

    return render_template(
        'compendium.html',
        form=form,
        form2=form2,
        data=data,
        counter=get_counter())


@app.route('/cc_item/<id>', methods=['GET', 'POST'])
@login_required
def cc_item(id):
    cci = CompendiumItem.query.filter_by(ci_id=id).first()
    form = EditContact(obj=cci)
    if form.submit.data:
        cci.dep_id = form.department.data.dep_id
        cci.name = form.name.data
        cci.phone = form.phone.data
        cci.desc = form.desc.data
        db.session.commit()
        flash('ЗБС!', 'success')
        return redirect(url_for('cc'))
    elif form.cancel.data:
        return redirect(url_for('cc'))

    elif request.method == 'GET':

        form.department.dep_id = cci.dep_id
        form.name.data = cci.name
        form.phone.data = cci.phone
        form.desc.data = cci.desc
    else:
        return redirect(url_for('cc'))
    return render_template('cc_item.html', id=id, form=form)


@app.route('/images/<filename>', methods=['GET'])
def images(filename):
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               filename, mimetype='image/png')


"""
@app.route('/add_adv', methods=['GET', 'POST'])
@login_required
def add_adv():
    form = AddAdPostForm()
    if form.validate_on_submit():
        f = form.photo.data
        guidstring = str(uuid.uuid4()) + '_'
        filename = secure_filename(f.filename).lower()
        path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), app.config['UPLOADS_PATH'])
        f.save(path + '/' + guidstring + filename)

        app.logger.info(guidstring + filename + ' saved to ' + path + '/')
        adpost = AdPost(title=form.title.data,
                        body=form.body.data,
                        image=guidstring + filename,
                        category_id=form.category.data.id,
                        price=form.price.data,
                        user_id=current_user.id
                        )
        db.session.add(adpost)
        db.session.commit()
        return redirect(url_for('advs_index'))
    return render_template('add_adv.html', form=form)


@app.route('/adpost_edit/<id>', methods=['GET', 'POST'])
@login_required
def adpost_edit(id):
    adpost = AdPost.query.filter_by(id=id).first_or_404()
    form = AdPostEditForm(obj=adpost)
    photoform = AdPostEditPhotoForm()
    if photoform.validate_on_submit():
        if photoform.submit.data:
            f = photoform.photo.data
            guidstring = str(uuid.uuid4()) + '_'
            filename = secure_filename(f.filename).lower()
            path = os.path.join(os.path.abspath(
                os.path.dirname(__file__)), app.config['UPLOADS_PATH'])
            f.save(path + '/' + guidstring + filename)
            app.logger.info(guidstring + filename + ' saved to ' + path + '/')

            adpost.image = guidstring + filename
            db.session.commit()
            return redirect(url_for('adpost', id=id))
        else:
            return redirect(url_for('advs_index'))
    if form.validate_on_submit():
        if form.submit.data:
            adpost.title = form.title.data,
            adpost.body = form.body.data,

            adpost.category_id = form.category.data.id,
            adpost.price = form.price.data

            db.session.commit()
            flash('Your changes have been saved.', 'warning')
            return redirect(url_for('adpost', id=id))
        else:
            return redirect(url_for('adpost', id=id))
    elif request.method == 'GET':
        form.title.data = adpost.title
        form.body.data = adpost.body

        form.category.id = adpost.category_id
        form.price.data = adpost.price

    return render_template('adpost_edit.html', adpost=adpost, form=form, photoform=photoform)


@app.route('/advs_index')
@login_required
def advs_index():
    adposts = AdPost.query.order_by(AdPost.created_at.desc()).all()
    categories = Category.query.all()
    return render_template('advs_index.html', adposts=adposts, categories=categories)
"""


# @app.route('/category/<id>')
# @login_required
# def advs_category(id):
#     adposts = AdPost.query.filter_by(
#         category_id=id).order_by(AdPost.created_at.desc())
#     categories = Category.query.all()
#     return render_template('advs_index.html', adposts=adposts, categories=categories)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.svg', mimetype='image/svg+xml')


# @app.route('/adpost/<id>')
# @login_required
# def adpost(id):
#     adpost = AdPost.query.filter_by(id=id).first_or_404()
#     return render_template('adpost_view.html', adpost=adpost)


@app.route('/static/uploads/<filename>')
def image(filename):
    path = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), app.config['UPLOADS_PATH'])

    return send_from_directory(path, filename)


"""
@app.route('/adpost_delete/<id>')
@login_required
def adpost_delete(id):
    adpost = AdPost.query.filter_by(id=id).first_or_404()
    db.session.delete(adpost)
    db.session.commit()
    flash('Объявление id: {} успешно удалено'.format(id), 'success')
    return redirect(url_for('advs_index'))

"""


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('vision'))


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('vision'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Успешно зарегистрирован', 'success')
#         return redirect(url_for('login'))
#     return render_template('register.html',
#                            title='Регистрация нового пользователя',
#                            form=form)


@app.route('/users/<username>')
@login_required
def user(username):
    users = User.query.all()
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=user).order_by(
        Post.timestamp.desc()).paginate(page, app.config['POST_PER_PAGE'], False)
    next_url = url_for('user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None

    return render_template('user.html', users=users, user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    avatarform = EditProfileAvatarForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    if avatarform.validate_on_submit():
        if avatarform.submit.data:
            f = avatarform.avatar.data
            guidstring = str(uuid.uuid4()) + '_'
            filename = secure_filename(f.filename).lower()
            path = os.path.join(os.path.abspath(
                os.path.dirname(__file__)), app.config['UPLOADS_PATH'])
            f.save(path + '/' + guidstring + filename)
            app.logger.info(guidstring + filename + ' saved to ' + path + '/')

            current_user.avatar = guidstring + filename
            db.session.commit()
            return redirect(url_for('user', username=current_user.username))
        else:
            return redirect(url_for('advs_index'))

    return render_template('edit_profile.html',
                           title='Редактирование профиля',
                           form=form, form2=avatarform)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} is not found'.format(username), 'warning')
        return redirect(url_for('vision'))

    if user == current_user:
        flash('Нельзя подписаться на самого себя', 'info')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('Подписались успешно', 'success')
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} is not found'.format(username), 'warning')
        return redirect(url_for('vision'))
    if user == current_user:
        flash('Нельзя отписаться от самого себя', 'info')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('Отписались успешно', 'success')
    return redirect(url_for('user', username=username))


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Проверьте почту', 'info')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/change_password/<token>', methods=['GET', 'POST'])
def change_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Пароль изменен', 'success')
        return redirect(url_for('login'))
    return render_template('change_password.html', form=form)


# @app.route('/chat')
# @login_required
# def chat():
#     """Chat room. The user's name and room must be stored in
#     the session."""
#     session['counter'] = 0
#     room = session['room'] = 'one'
#     name = session['name'] = current_user.username
#     room = session.get('room', '')
#     if name == '' or room == '':
#         return redirect(url_for('.index'))
#     return render_template('chat.html', name=name, room=room)


# # EVENTS
# @socketio.on('joined', namespace='/chat')
# def joined(message):
#     """Sent by clients when they enter a room.
#     A status message is broadcast to all people in the room."""
#     room = session.get('room')
#     join_room(room)

#     emit('status', {'msg': session.get('name') + ' вошел в чат.'}, room=room)


# @socketio.on('text', namespace='/chat')
# def text(message):
#     """Sent by a client when the user entered a new message.
#     The message is sent to all people in the room."""
#     if len(message['msg']) != 0:

#         app.logger.info(message['msg'])
#         room = session.get('room')
#         emit('message', {'msg': session.get('name') +
#                          ':' + message['msg']}, room=room)


# @socketio.on('left', namespace='/chat')
# def left(message):
#     """Sent by clients when they leave a room.
#     A status message is broadcast to all people in the room."""
#     room = session.get('room')
#     leave_room(room)
#     session['counter'] -= 1
#     emit('status', {'msg': session.get('name') +
#                     ' has left the room.'}, room=room)


@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    form = AddCategoryForm()
    if form.validate_on_submit():
        cat = Category(name=form.category.data)
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for('info'))

    return render_template('add_category.html', form=form)


@app.route('/info', methods=['GET'])
@login_required
def info():
    page = request.args.get('page', 1, type=int)
    categories = Category.query.all()
    search_form = SearchInsForm()

    # if not search_form.validate():
    """
    ins = Instruction.query.paginate(
    page, app.config['POST_PER_PAGE'], False)

    next_url = url_for(
        'info', page=ins.next_num) if ins.has_next else None
    prev_url = url_for(
        'info', page=ins.prev_num) if ins.has_prev else None

    return render_template('info.html', ins=ins.items, categories=categories, search_form=search_form,
        next_url=next_url,
        prev_url=prev_url)
    """

    keyword = request.args.get('search')
    if keyword is None:
        keyword = ''

    query = db.session.query(Instruction).filter_by(deleted=False)

    s = search(query, keyword)

    ins = s.paginate(page, app.config['POST_PER_PAGE'], False)
    next_url = url_for(
        'info', page=ins.next_num) if ins.has_next else None
    prev_url = url_for(
        'info', page=ins.prev_num) if ins.has_prev else None

    return render_template(
        'info.html',
        ins=ins.items, categories=categories,
        search_form=search_form,
        next_url=next_url,
        prev_url=prev_url,
        counter=get_counter())


@app.route('/info_cat/<category_id>', methods=['GET'])
@login_required
def info_cat(category_id):
    page = request.args.get('page', 1, type=int)
    ins = Instruction.query.filter_by(category_id=category_id, deleted=False).paginate(
        page, app.config['POST_PER_PAGE'], False)
    categories = Category.query.all()

    next_url = url_for(
        'info_cat', page=ins.next_num, category_id=category_id) if ins.has_next else None
    prev_url = url_for(
        'info_cat', page=ins.prev_num, category_id=category_id) if ins.has_prev else None

    return render_template('info_cat.html', ins=ins.items, categories=categories, next_url=next_url,
                           prev_url=prev_url)


@app.route('/add_info', methods=['POST', 'GET'])
def add_info():
    form = AddInstruction()
    if form.validate_on_submit():
        if form.submit.data:
            i = Instruction(
                trouble=form.trouble.data,
                theme=form.theme.data,
                category_id=form.category.data.id
            )
            db.session.add(i)
            db.session.commit()
            flash('Добавлено ЗБС', 'success')
            return redirect(url_for('info'))
        elif form.cancel.data:
            return redirect(url_for('info'))
    return render_template('add_info.html', form=form)


@app.route('/info_view/<id>', methods=['GET'])
def info_view(id):
    info = Instruction.query.filter_by(id=id).first_or_404()
    return render_template('info_view.html', info=info)


@app.route('/info_edit/<id>', methods=['GET', 'POST'])
def info_edit(id):
    info = Instruction.query.filter_by(id=id).first_or_404()
    form = EditInstruction(obj=info)
    if form.validate_on_submit():
        if form.submit.data:
            info.category_id = form.category.data.id
            info.theme = form.theme.data
            info.trouble = form.trouble.data
            db.session.commit()
            return redirect(url_for('info_view', id=info.id))
        elif form.cancel.data:
            return redirect(url_for('info'))

    return render_template('info_edit.html', info=info, form=form)


# @app.route('/info_deleted', methods=['GET'])
# def info_deleted():
#     page = request.args.get('page', 1, type=int)
#     ins = Instruction.query.filter_by(deleted=True).paginate(
#         page, app.config['POST_PER_PAGE'], False)
#     categories = Category.query.all()

#     next_url = url_for(
#         'info_cat', page=ins.next_num, category_id=category_id) if ins.has_next else None
#     prev_url = url_for(
#         'info_cat', page=ins.prev_num, category_id=category_id) if ins.has_prev else None

#     return render_template('info_deleted.html', ins=ins.items, categories=categories, next_url=next_url,
#                            prev_url=prev_url)


@app.route('/info_del/<id>')
def info_del(id):
    ins = Instruction.query.filter_by(id=id).first_or_404()
    ins.deleted = True
    db.session.commit()
    flash('Инструкция перемещена в Удаленные', 'success')
    return redirect(url_for('info'))


@app.route('/info_res/<id>')
def info_res(id):
    ins = Instruction.query.filter_by(id=id).first_or_404()
    ins.deleted = False
    db.session.commit()
    flash('Инструкция восстановлена', 'success')
    return redirect(url_for('info'))


@app.route('/reports', methods=['GET', 'POST'])
def reports():

    userid = current_user.id
    form = AddReportForm()
    reports = Report.query.all()
    days = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
    if form.validate_on_submit():
        report = Report(
            user_id=current_user.id,
            date=form.date.data,
            report_body=form.report_body.data)
        db.session.add(report)
        db.session.commit()
        return redirect(url_for('reports'))

    return render_template('reports.html', form=form, reports=reports)


# # SERVERSIDE BEGIN
# from app.serverside_table import ServerSideTable
# from app import table_schemas


# class TableBuilder(object):

#     def collect_data_clientside(self, status):
#         return {'data': AtlasQueueConnection().get_messages_queue(status) }

#     def collect_data_serverside(self, request, status):
#         data = AtlasQueueConnection().get_messages_queue(status)
#         columns = table_schemas.SERVERSIDE_TABLE_COLUMNS
#         return ServerSideTable(request, data, columns).output_result()

# table_builder = TableBuilder()


# @app.route("/clientside_table", methods=['GET'])
# def clientside_table_content():
#     data = table_builder.collect_data_clientside()
#     return jsonify(data)


# @app.route("/serverside_table/<status>", methods=['GET'])
# def serverside_table_content(status):
#     data = table_builder.collect_data_serverside(request, status)
#     return jsonify(data)
# # SERVERSIDE END

@app.route('/get_users/<enterprise>', methods=['GET', 'POST'])
@login_required
def get_users(enterprise):

    form = NewDNSubmit()

    if form.validate_on_submit():
        connect = psycopg2.connect(host=form.host_ip.data,
                                   dbname="Integro.Security",
                                   user="postgres",
                                   password=form.password.data)
        text = form.dnstring.data.split('\n')
        text.reverse()
        text = ','.join(text).replace('Phone = ', '2.5.4.20=\\').replace(
            ' = ', '=').replace('\r', '').replace(';', ',')
        dn = text
        if connect:
            with connect.cursor() as cursor:
                cursor.execute("""
                    UPDATE t_rules
                    SET value = '{}'
                    WHERE rule_id = 5324
                    AND id = '{}'""".format(dn, form.user_id.data))
                connect.commit()

        return redirect(url_for('get_users', enterprise=enterprise))

    elif request.method == 'GET':
        conn1 = psycopg2.connect(
            host='10.10.2.18',
            dbname='Support',
            user='postgres',
            password='Abu pfgjvybim'
        )
        with conn1.cursor() as cursor:
            cursor.execute("""
                        SELECT owner_ip
                        FROM t_information
                        WHERE enterprise = '{}'
                        """.format(enterprise))
            host_ip = cursor.fetchone()[0]

        password = Contact.query.filter_by(
            c_enterprise_id=enterprise).first().password
        if password != '0':
            conn2 = psycopg2.connect(
                host=host_ip,
                dbname='Integro.Security',
                user='postgres',
                password=password
            )
            if conn2:
                with conn2.cursor() as cursor:
                    cursor.execute("""SELECT u.id, u.username, u.password, u.locked, r.value  FROM t_rules r
                                    INNER JOIN t_user u ON u.id = r.id
                                    WHERE r.rule_id = 5324 AND u.username != 'Admin'""")
                    data = cursor.fetchall()
            else:
                data = None
        else:
            data = None

        return render_template('server_users.html', data=data, password=password, host_ip=host_ip, form=form)


def getDNStrings():
    with pg.connect(
        host='10.10.2.209',
        dbname='DN_Container',
        user='postgres',
        password='Abu pfgjvybim'
    ) as conn:
        if conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM dnstring WHERE active = True ORDER BY rec_date DESC")
                results = cursor.fetchall()
                l = []
                for res in results:

                    result = {
                        "id": res[0],
                        "dn": res[1],
                        "rec_date": res[2],
                        "time_create": res[3],
                        "active": res[4]
                    }
                    print(result)
                    l.append(result)
                return l
        else:
            return None


@app.route('/dnstrings', methods=['GET', 'POST'])
def dnstrings():
    dnstrings = getDNStrings()
    return render_template('dnstrings.html', dnstrings=dnstrings, counter=get_counter())

@app.route('/dnstring_update', methods=['GET', 'POST'])
def dnstring_update():
    data = request.get_json(force=False)
    id = data['id']
    text = data['text']
    with pg.connect(
        host='10.10.2.209',
        dbname='DN_Container',
        user='postgres',
        password='Abu pfgjvybim'
    ) as conn:
        if conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""UPDATE dnstring SET dnstring = '{text}' WHERE id = '{id}'""")
    return redirect(url_for('dnstring_view', id=id))

@app.route('/dnstring_view/<id>', methods=['GET', 'POST'])
def dnstring_view(id):
    
    with pg.connect(
        host='10.10.2.216',
        dbname='Avrora.OBLUPR',
        user='integrist',
        port=6432,
        password='Administrator$'
    ) as conn, pg.connect(
        host='10.10.2.209',
        dbname='DN_Container',
        user='postgres',
        password='Abu pfgjvybim'
    ) as conn2:
        if conn2 and conn:
            with conn.cursor() as cursor0, conn2.cursor() as cursor1:
                cursor1.execute(
                    f"SELECT id, dnstring FROM dnstring WHERE active = True AND id = '{id}';")
                dn = cursor1.fetchone()

                dn = {"id": dn[0],
                      "dnstring": dn[1]}

                # print(dn["dnstring"])
                fi = re.search(
                    r"(?<=CN=)(.*) (.*),G=(.*)(?=,SERIALNUMBER)|(?<=,CN=)(.*) (.*)(?=,SERIALNUMBER)", dn["dnstring"])
                # print(fi)

                name = fi.group(1)
                second = fi.group(2)
                middle = fi.group(3)
                
                print(middle is not None)
                if middle is not None:
                    print(name, second, middle)
                    cursor0.execute(f"""SELECT id, first_name || ' ' || last_name || ' ' || middle_name FROM t_xml_person
                                    WHERE first_name ILIKE '%{name}%' AND last_name ILIKE '%{second}%' AND middle_name ILIKE '%{middle}%' AND del_rec = FALSE""")
                    person_ids = cursor0.fetchall()
                else:
                    name = fi.group(4)
                    second = fi.group(5)
                    print(name, second)
                    cursor0.execute(f"""SELECT id, first_name || ' ' || last_name FROM t_xml_person
                                    WHERE first_name ilike '%{name}%' AND last_name ilike '%{second}%' AND del_rec = FALSE""")
                    person_ids = cursor0.fetchall()

                print(person_ids, len(person_ids))
                current_dn = None
                login = []
                lg = {}

                if person_ids is not None and len(person_ids) > 0:
                    # ('id',) в ('id') если одно значение, если больше то ('id','id')
                    # persons = str(tuple( [x[0] for x in person_ids] )).replace(',', '') if len(person_ids) == 1 else str(tuple( [x[0] for x in person_ids] ))

                    for pers_id, fio in person_ids:
                        lg[pers_id] = {}
                        lg[pers_id]["fio"] = fio
                        # print(">>>",pers_id)
                        query = f""" SELECT id, xml_data, (xpath('//Login/text()', xml_data))[1]::TEXT FROM t_xml_user 
                                WHERE (xpath('//Employee/text()', xml_data))[1]::TEXT::UUID IN 
                                    (
                                    SELECT id FROM t_xml_employee 
                                    WHERE owner_id::UUID = '{pers_id}'
                                            AND del_rec = FALSE
                                    ) 
                                AND del_rec = FALSE
                            """
                        cursor0.execute(query)
                        result = cursor0.fetchall()
                        lg[pers_id]["login"] = [x[2] for x in result]
                        lg[pers_id]["user_id"] = [x[0] for x in result]
                        for user in result:
                            cursor0.execute(
                                f"SELECT xml_data, id FROM t_xml_permission WHERE parent_id = '{user[0]}' AND xml_data::TEXT ILIKE '%DN%' AND del_rec = False")
                            xml_data = cursor0.fetchone()
                            print("XML", xml_data)
                            if xml_data is not None:
                                current_dn = re.search(
                                    r"(?<=&lt;DN&gt;)(.*)(?=&lt;\/DN&gt;)", xml_data[0])
                                print(current_dn, xml_data[0])
                                lg[pers_id]["permission"] = xml_data[1]
                                lg[pers_id]["current_dn"] = current_dn.group(1) if current_dn is not None else 'Ошибка DN строки, требуется перезапись\пересохранение строки вручную.'
                                
                    # query = f""" SELECT id, xml_data, (xpath('//Login/text()', xml_data))[1]::TEXT FROM t_xml_user
                    #             WHERE (xpath('//Employee/text()', xml_data))[1]::TEXT::UUID IN
                    #                 (
                    #                 SELECT id FROM t_xml_employee
                    #                 WHERE owner_id::UUID IN
                    #                         {persons}
                    #                      AND del_rec = FALSE
                    #                 )
                    #             AND del_rec = FALSE
                    #         """
                    # print(query)
                    # cursor0.execute(query)
                    # result = cursor0.fetchall()

                    # for res in result:
                    #     user_id = res[0]
                    #     login.append(res[2])
                    #     cursor0.execute(f"SELECT xml_data FROM t_xml_permission WHERE parent_id = '{user_id}' AND xml_data::TEXT ILIKE '%DN%'")
                    #     xml_data = cursor0.fetchone()
                    #     print(xml_data)
                    #     current_dn = re.search(r"(?<=&lt;DN&gt;)(.*)(?=&lt;\/DN&gt;)", xml_data[0])
                    #     current_dn = current_dn.group(1)
                    # print("LG", lg)
                    return render_template('dnstring_view.html', persons=person_ids, dn=dn, users=lg, current_dn=current_dn)
                return render_template('dnstring_view.html', persons=[], dn=dn, users=login, current_dn=current_dn)

@app.route('/create_dn/<id>/<user_id>', methods=['GET', 'POST'])
def create_dn(id, user_id):
    with pg.connect(
        host='10.10.2.209',
        dbname='DN_Container',
        user='postgres',
        password='Abu pfgjvybim'
    ) as conn, pg.connect(
        host='10.10.2.216',
        dbname='Avrora.OBLUPR',
        user='integrist',
        port=6432,
        password='Administrator$'
    ) as odo:
        
        with conn.cursor() as cursor, odo.cursor() as odursor:
            cursor.execute(f"""SELECT dnstring FROM dnstring WHERE id = '{id}'""")
            dnstring = cursor.fetchone()
            permission_id = uuid.uuid4()
            query = f"""INSERT INTO t_xml_permission("id", "parent_id", "owner_id", "type", "xml_data", "user_id", "rec_date", "status", "del_rec") VALUES ('{permission_id}', '{user_id}', NULL, 'Avrora.Objects.Security.SecurityPermission', '<?xml version="1.0" standalone="yes"?><Avrora.Objects.Security.SecurityPermission><ValueTypeFullName>Avrora.Objects.Modules.Docflow.CommonObjects.CspContainerRule</ValueTypeFullName><BDValue>&lt;Avrora.Objects.Modules.Docflow.CommonObjects.CspContainerRule&gt;
  &lt;Container&gt;profile://ESEDO004&lt;/Container&gt;
  &lt;DN&gt;{dnstring[0]}&lt;/DN&gt;
  &lt;ProviderType&gt;0&lt;/ProviderType&gt;
&lt;/Avrora.Objects.Modules.Docflow.CommonObjects.CspContainerRule&gt;</BDValue><RuleId>5327</RuleId></Avrora.Objects.Security.SecurityPermission>', '5b592be1-2866-4a5c-9b01-978fdf2dd48e', '2021-06-30 15:22:43.055239', 0, 'f');"""
            # print(query)
            odursor.execute(query)
            odursor.execute(f"SELECT id, xml_data FROM t_xml_user WHERE id = '{user_id}'")
            user = odursor.fetchone()

            xml_data = user[1]
            # print(user[1])
            parsed_xml = ET.fromstring(xml_data)
            
            for child in parsed_xml:
                
                if child.tag == 'PermissionList':
                    if child.text is not None or child.text != "None":
                        child.text = f"''{permission_id}''"
                    else:
                        child.text = f"{child.text},''{permission_id}''"
                        
                    # print(child.text)

            xml_data = ET.tostring(parsed_xml, encoding='unicode', method='xml')
            q = f"""UPDATE t_xml_user SET xml_data = '<?xml version="1.0" standalone="yes"?>{xml_data}' WHERE id = '{user_id}'"""
            print(q)
            odursor.execute(q)
            


            
    return redirect(url_for('dnstring_view', id=id))

@app.route('/update_dn/<id>/<permission>', methods=['GET', 'POST'])
def update_dn(id, permission):
    # print(id, permission)
    with pg.connect(
        host='10.10.2.216',
        dbname='Avrora.OBLUPR',
        user='integrist',
        port=6432,
        password='Administrator$'
    ) as odo, pg.connect(
        host='10.10.2.209',
        dbname='DN_Container',
        user='postgres',
        password='Abu pfgjvybim'
    ) as obl:
        with odo.cursor() as odo_cursor, obl.cursor() as obl_cursor:
            obl_cursor.execute(
                f"""SELECT dnstring FROM dnstring WHERE id = '{id}';""")
            dnstring = obl_cursor.fetchone()
            # print(dnstring)

            permission_string = f"""<?xml version="1.0" standalone="yes"?><Avrora.Objects.Security.SecurityPermission><ValueTypeFullName>Avrora.Objects.Modules.Docflow.CommonObjects.CspContainerRule</ValueTypeFullName><BDValue>&lt;Avrora.Objects.Modules.Docflow.CommonObjects.CspContainerRule&gt;
  &lt;Container&gt;profile://ESEDO004&lt;/Container&gt;
  &lt;DN&gt;{dnstring[0]}&lt;/DN&gt;
  &lt;ProviderType&gt;0&lt;/ProviderType&gt;
&lt;/Avrora.Objects.Modules.Docflow.CommonObjects.CspContainerRule&gt;</BDValue><RuleId>5327</RuleId></Avrora.Objects.Security.SecurityPermission>"""

            odo_cursor.execute(
                f"""UPDATE t_xml_permission SET xml_data = '{permission_string}' WHERE id = '{permission}'""")

            return redirect(url_for('dnstring_view', id=id))


@app.route('/deactivate_dn/<id>', methods=['GET', 'POST'])
def deactivate_dn(id):
    with pg.connect(
        host='10.10.2.209',
        dbname='DN_Container',
        user='postgres',
        password='Abu pfgjvybim'
    ) as conn:
        if conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"UPDATE dnstring SET active = False WHERE id = '{id}';")
                conn.commit()
                return redirect(url_for('dnstrings'))
        else:

            return redirect(url_for('dnstrings'))


@app.route('/person_check', methods=['GET', 'POST'])
def person_check():
    return render_template("person_check.html", counter=get_counter())



@app.route('/look_for_person', methods=['GET', 'POST'])
def look_for_person():
    with pg.connect(
        host='10.10.2.216',
        dbname='Avrora.OBLUPR',
        user='integrist',
        port=6432,
        password='Administrator$'
    ) as odo:
        with odo.cursor() as cursor:
            
            data = request.get_json(force=False)
            # print(data)
            first_name = data['first_name']
            last_name=data['last_name']
            
            if last_name != '':
                cursor.execute(
                f"""SELECT id, first_name, last_name, middle_name FROM t_xml_person WHERE first_name ILIKE '%{first_name}%' AND last_name ILIKE '%{last_name}%' AND del_rec = FALSE LIMIT 10""")
            else:
                cursor.execute(
                    f"""SELECT id, first_name, last_name, middle_name FROM t_xml_person WHERE first_name ILIKE '%{first_name}%' AND del_rec = FALSE LIMIT 10 """)
            person = cursor.fetchall()

            
            
            # print(person)
            person_with_info = []
            for p in person:
                
                # print(p)
                query = f""" SELECT id, (xpath('//Enterprise/text()', xml_data))[1]::TEXT, (xpath('//Login/text()', xml_data))[1]::TEXT FROM t_xml_user 
                            WHERE (xpath('//Employee/text()', xml_data))[1]::TEXT::UUID IN 
                                (
                                SELECT id FROM t_xml_employee 
                                WHERE owner_id::UUID = '{p[0]}'
                                        AND del_rec = FALSE
                                ) 
                            AND del_rec = FALSE
                        """
                cursor.execute(query)
                user = cursor.fetchone()
                if user is not None:
                    p += user
                else:
                    p += ('','','')
                person_with_info.append(p)
                
            return jsonify(person_with_info)

@app.route('/person_view/<person_id>', methods=['GET', 'POST'])
def person_view(person_id):
    with pg.connect(
        host='10.10.2.216',
        dbname='Avrora.OBLUPR',
        user='integrist',
        port=6432,
        password='Administrator$'
    ) as odo:
        with odo.cursor() as cursor:
            cursor.execute(f"SELECT id, first_name, last_name, middle_name, rec_date, del_rec FROM t_xml_person WHERE id = '{person_id}'")
            person = cursor.fetchone()

            cursor.execute(f""" SELECT id, parent_id, (xpath('//Login/text()', xml_data))[1]::TEXT, xml_data, rec_date, del_rec FROM t_xml_user 
                            WHERE (xpath('//Employee/text()', xml_data))[1]::TEXT::UUID IN 
                                (
                                SELECT id FROM t_xml_employee 
                                WHERE owner_id::UUID = '{person_id}'
                                        AND del_rec = FALSE
                                ) 
                            AND del_rec = FALSE
                        """)
            user = cursor.fetchall()

            cursor.execute(f"""SELECT * FROM t_xml_employee WHERE owner_id = '{person_id}' AND del_rec = False""")
            employee = cursor.fetchall()
    return render_template("person_view.html", person=person, user=user, employee=employee)

@app.route('/user_view/<user_id>', methods=['GET', 'POST'])
def user_view(user_id):
    with pg.connect(
        host='10.10.2.216',
        dbname='Avrora.OBLUPR',
        user='integrist',
        port=6432,
        password='Administrator$'
    ) as odo:
        with odo.cursor() as cursor:
            cursor.execute(f"SELECT * FROM t_xml_user WHERE id = '{user_id}'")
            user = cursor.fetchone()
    return render_template("user_view.html", user=user)

@app.route('/add_current_user/<person_id>/<workplace>/<enterprise>/<employee>', methods=['GET', 'POST'])
def add_current_user(person_id, workplace, enterprise, employee):
    # TODO: Добавить проверку логинов на дубликат
    # TODO: После проверки добавлять цифру к Логину

    with pg.connect(
        host='10.10.2.216',
        dbname='Avrora.OBLUPR',
        user='integrist',
        port=6432,
        password='Administrator$'
    ) as odo:
        with odo.cursor() as cursor:
            cursor.execute(f"SELECT id, first_name, last_name, middle_name FROM t_xml_person WHERE id = '{person_id}'")
            person = cursor.fetchone()
            print(person)
            if person[3]:
                login = person[1].capitalize() + person[2][0] + person[3][0]
            else:
                login = person[1].capitalize() + person[2][0]
            new_user_id = uuid.uuid4()
            user_query = f"""INSERT INTO "public"."t_xml_user"("id", "parent_id", "owner_id", "type", "xml_data", "user_id", "rec_date", "status", "del_rec") 
            VALUES ('{new_user_id}', '{enterprise}', NULL, 'Avrora.Objects.Security.SecurityUser', '<?xml version="1.0" standalone="yes"?><Avrora.Objects.Security.SecurityUser><Enterprise>{enterprise}</Enterprise><Employee>{employee}</Employee><Login>{login}</Login><Password>8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92</Password><Locked>False</Locked><PermissionList></PermissionList><Internal>False</Internal></Avrora.Objects.Security.SecurityUser>', 'a5b78390-b2bc-4f7c-9efb-549b4a6e2c93', '2021-10-21 18:00:00.111111', 0, 'f');
"""         
            cursor.execute(user_query)
            return redirect(url_for('person_view', person_id=person_id))

@app.route('/add_person', methods=['GET', 'POST'])
def add_person():
    with pg.connect(
        host='10.10.2.216',
        dbname='Avrora.OBLUPR',
        user='integrist',
        port=6432,
        password='Administrator$'
    ) as odo, pg.connect(
        host='10.10.2.209',
        dbname='DN_Container',
        user='postgres',
        password='Abu pfgjvybim'
    ) as obl:
        with odo.cursor() as odo_cursor, obl.cursor() as obl_cursor:
            data = request.get_json(force=False)
            # print(data)
            obl_cursor.execute(f"""SELECT dnstring FROM dnstring WHERE id='{data["id"]}'""")
            dn = obl_cursor.fetchone()
            new_person_id = uuid.uuid4()

            fi = re.search(
                r"(?<=CN=)(.*) (.*),G=(.*)(?=,SERIALNUMBER)|(?<=,CN=)(.*) (.*)(?=,SERIALNUMBER)", dn[0] )

            name = fi.group(1)
            second = fi.group(2)
            middle = fi.group(3)
            print(name, second, middle)
            
            if middle is not None:

                query = f"""INSERT INTO "public"."t_xml_person"("id", "parent_id", "owner_id", "code", "first_name", "last_name", "middle_name", "birth_date", "sex", "resident", "type", "xml_data", "user_id", "rec_date", "status", "del_rec") 
            VALUES ('{new_person_id}', '00000000-0000-0000-0000-000000000000', NULL, 0, '{name}', '{second}', '{middle}', NULL, 0, 'f', 'Avrora.Objects.Common.Person', '<?xml version="1.0" standalone="yes"?><Avrora.Objects.Common.Person><AddressId>0</AddressId></Avrora.Objects.Common.Person>', '288b2765-6ff8-4a88-81fc-92a25f7e18fb', '2021-04-15 12:12:12.123456', 0, 'f');
"""
            else:
                query = f"""INSERT INTO "public"."t_xml_person"("id", "parent_id", "owner_id", "code", "first_name", "last_name", "middle_name", "birth_date", "sex", "resident", "type", "xml_data", "user_id", "rec_date", "status", "del_rec") 
            VALUES ('{new_person_id}', '00000000-0000-0000-0000-000000000000', NULL, 0, '{name}', '{second}', '', NULL, 0, 'f', 'Avrora.Objects.Common.Person', '<?xml version="1.0" standalone="yes"?><Avrora.Objects.Common.Person><AddressId>0</AddressId></Avrora.Objects.Common.Person>', '288b2765-6ff8-4a88-81fc-92a25f7e18fb', '2021-04-15 12:12:12.123456', 0, 'f');
"""

            odo_cursor.execute(query)
            
            return jsonify({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/person_add_from_check', methods=['POST', 'GET'])
def person_add_from_check():
    with pg.connect(
        host='10.10.2.216',
        dbname='Avrora.OBLUPR',
        user='integrist',
        port=6432,
        password='Administrator$'
    ) as odo:
        with odo.cursor() as cursor:
            data = request.get_json(force=False)
            print(data)
            first = data['first_name']
            last = data['last_name']
            middle = data['middle_name']
            new_person_id = uuid.uuid4()
            if middle is not None:
                query = f"""INSERT INTO "public"."t_xml_person"("id", "parent_id", "owner_id", "code", "first_name", "last_name", "middle_name", "birth_date", "sex", "resident", "type", "xml_data", "user_id", "rec_date", "status", "del_rec") 
            VALUES ('{new_person_id}', '00000000-0000-0000-0000-000000000000', NULL, 0, '{first}', '{last}', '{middle}', NULL, 0, 'f', 'Avrora.Objects.Common.Person', '<?xml version="1.0" standalone="yes"?><Avrora.Objects.Common.Person><AddressId>0</AddressId></Avrora.Objects.Common.Person>', '288b2765-6ff8-4a88-81fc-92a25f7e18fb', '2021-04-15 12:12:12.123456', 0, 'f');
"""
            else:
                query = f"""INSERT INTO "public"."t_xml_person"("id", "parent_id", "owner_id", "code", "first_name", "last_name", "middle_name", "birth_date", "sex", "resident", "type", "xml_data", "user_id", "rec_date", "status", "del_rec") 
            VALUES ('{new_person_id}', '00000000-0000-0000-0000-000000000000', NULL, 0, '{first}', '{last}', '', NULL, 0, 'f', 'Avrora.Objects.Common.Person', '<?xml version="1.0" standalone="yes"?><Avrora.Objects.Common.Person><AddressId>0</AddressId></Avrora.Objects.Common.Person>', '288b2765-6ff8-4a88-81fc-92a25f7e18fb', '2021-04-15 12:12:12.123456', 0, 'f');
"""

            cursor.execute(query)
            # return redirect(url_for('person_view', person_id=new_person_id ))
            return jsonify({'success':True, 'person': new_person_id}), 200, {'ContentType':'application/json'} 

@app.route('/get_enterprises/', methods=['GET'])
def get_enterprises():
    q = request.args.get('q')
    if q is None:
        q = ''
    print(q)

    with pg.connect(
        host='10.10.2.216',
        dbname='Avrora.OBLUPR',
        user='integrist',
        port=6432,
        password='Administrator$'
    ) as odo:
        with odo.cursor() as cursor:
            cursor.execute(f"SELECT id, name ->> 'ru-RU' as name FROM t_xml_community WHERE name ->> 'ru-RU' ILIKE '%{q}%' AND type = 'Avrora.Objects.Modules.EMS.Enterprise, Avrora.Objects.Common.Community' ORDER BY name ASC")
            enterprises = cursor.fetchall()

            r = []
            for id, text in enterprises:
                # print(id, text)
                res = {}
                res["id"] = id
                res["text"] = text + ' ' + id
                # print(res)
                r.append(res)
            
            # print(r)
            return jsonify({"results": r, "pagination": {"more": False}}) , 200, {'ContentType':'application/json'}

@app.route('/get_jobtitles', methods=['GET'])
def get_jobtitles():
    q = request.args.get('q')
    if q is None:
        q = ''
    print(q)

    with pg.connect(
        host='10.10.2.216',
        dbname='Avrora.OBLUPR',
        user='integrist',
        port=6432,
        password='Administrator$'
    ) as odo:
        with odo.cursor() as cursor:
            cursor.execute(f"SELECT id, (xpath('//Name/text()', xml_data))[1] as n FROM t_xml_jobtitle WHERE (xpath('//Name/text()', xml_data))[1]::TEXT ILIKE '%{q}%' ")
            jobtitles = cursor.fetchall()

            r = []
            for id, text in jobtitles:
                # print(id, text)
                res = {}
                res["id"] = id
                res["text"] = text + ' ' + id
                # print(res)
                r.append(res)
            
            # print(r)
            return jsonify({"results": r, "pagination": {"more": False}}) , 200, {'ContentType':'application/json'}

@app.route('/add_employee', methods=['POST'])
def add_employee():
    req = request.get_json(force=False)
    # print(req)
    enterprise = req['enterprise']
    person_id = req['person']
    jobtitle_id = req['jobtitle']
    data = {"enterprise": enterprise, "person": person_id}

    new_employee_id = uuid.uuid4()
    new_workplace_id = uuid.uuid4()

    employee_query = f"""INSERT INTO "public"."t_xml_employee"("id", "parent_id", "owner_id", "enterprise_id", "from_date", "type", "xml_data", "user_id", "rec_date", "status", "del_rec") VALUES ('{new_employee_id}', '{new_workplace_id}', '{person_id}', '{enterprise}', '{datetime.now()}', 'Avrora.Objects.Modules.EMS.Employee', '<?xml version="1.0" standalone="yes"?><Avrora.Objects.Modules.EMS.Employee><WorkPlace>{new_workplace_id}</WorkPlace><Person>{person_id}</Person><TabNumber>0</TabNumber><WorkKind>1</WorkKind><WorkView>1</WorkView></Avrora.Objects.Modules.EMS.Employee>', '288b2765-6ff8-4a88-81fc-92a25f7e18fb', '{datetime.now()}', 0, 'f');"""
    workplace_query = f"""INSERT INTO "public"."t_xml_community"("id", "parent_id", "owner_id", "head", "name", "shortname", "type", "xml_data", "user_id", "rec_date", "status", "del_rec") VALUES ('{new_workplace_id}', '{enterprise}', '{enterprise}', '{new_employee_id}', '{{}}', '{{}}', 'Avrora.Objects.Modules.EMS.WorkPlace, Avrora.Objects.Common.Community', '<?xml version="1.0" standalone="yes"?><Avrora.Objects.Modules.EMS.WorkPlace><Enterprise>{enterprise}</Enterprise><Employee>{new_employee_id}</Employee><JobTitle>{jobtitle_id}</JobTitle><StaffRecord>True</StaffRecord><CommunityParent>{enterprise}</CommunityParent></Avrora.Objects.Modules.EMS.WorkPlace>', '288b2765-6ff8-4a88-81fc-92a25f7e18fb', '{datetime.now()}', 0, 'f');"""

    print(employee_query)
    print()
    print(workplace_query)
    with pg.connect(
        host='10.10.2.216',
        dbname='Avrora.OBLUPR',
        user='integrist',
        port=6432,
        password='Administrator$'
    ) as odo:
        with odo.cursor() as cursor:
            cursor.execute(employee_query)
            cursor.execute(workplace_query)
            data["success"] = True
    return jsonify(data, 200, {'ContentType':'application/json'})

@app.route('/shtat/<enterprise>', methods=['GET'])
def shtat(enterprise):
    with pg.connect(
        host='10.10.2.216',
        dbname='Avrora.OBLUPR',
        user='integrist',
        port=6432,
        password='Administrator$'
    ) as odo:
        with odo.cursor() as cursor:
            query = f"""WITH RECURSIVE shtat AS (
                    SELECT
                        t_xml_community.ID,
                        t_xml_community.parent_id,
                        t_xml_community.NAME,
                        t_xml_community.TYPE,
                        t_xml_community.xml_data::TEXT,
                        t_xml_community.rec_date,
                        t_xml_community.del_rec 
                    FROM
                        t_xml_community 
                    WHERE
                        ID = '{enterprise}' UNION
                    SELECT
                        t_xml_community.ID,
                        t_xml_community.parent_id,
                        t_xml_community.NAME,
                        t_xml_community.TYPE,
                        t_xml_community.xml_data::TEXT,
                        t_xml_community.rec_date,
                        t_xml_community.del_rec 
                    FROM
                        t_xml_community
                        JOIN shtat ON t_xml_community.parent_id = shtat.ID 
                    ) SELECT
                    shtat.ID,
                    shtat.parent_id,
                    
                    shtat.NAME,
                    shtat.TYPE,
                    shtat.xml_data,
                    shtat.rec_date,
                    shtat.del_rec 
                FROM
                    shtat"""
                    
            query_one = f"SELECT id, parent_id, name, type, xml_data, del_rec FROM t_xml_community WHERE id = '{enterprise}'"
            cursor.execute(query_one)
            objects = cursor.fetchall()
            return render_template('shtat.html', objects=objects)
    
@app.route('/get_shtat_children/<enterprise>', methods=['GET', 'POST'])
def get_shtat_children(enterprise):
    with pg.connect(
        host='10.10.2.216',
        dbname='Avrora.OBLUPR',
        user='integrist',
        port=6432,
        password='Administrator$'
    ) as odo:
        with odo.cursor() as cursor:
            q = f"""SELECT id, parent_id, name->>'ru-RU', type, xml_data, del_rec FROM t_xml_community WHERE parent_id = '{enterprise}' and del_rec = False"""
            cursor.execute(q)
            res = cursor.fetchall()
            return jsonify({'data': res, 'success': True})