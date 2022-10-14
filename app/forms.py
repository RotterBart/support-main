from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, ValidationError, IntegerField, FileField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Required
from wtforms.fields.html5 import DateField
from flask_login import current_user
from app.models import *
from wtforms.widgets import TextArea
from flask import request
from flask_ckeditor import CKEditorField

class DnTransform(FlaskForm):
    dnForm = TextAreaField('DN', validators=[Length(min=0, max=512)])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повтор пароля',
                              validators=[DataRequired(),
                                          EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Такое имя существует.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Такой почтовый ящик существует.')


class EditProfileForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    about_me = TextAreaField('Инфо', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Такое имя существует.')


class EditProfileAvatarForm(FlaskForm):
    avatar = FileField(
        'Убедительная просьба размещать аватарки размером 200х200, иначе бан',
        validators=[
            FileRequired(),
            FileAllowed(['jpg', 'png', 'bmp'], 'Images only!')
        ])
    submit = SubmitField('Изменить аватар')


class PostForm(FlaskForm):
    post = TextAreaField('Введите сообщение:',
                         validators=[DataRequired(),
                                     Length(min=1, max=250)])
    submit = SubmitField('Отправить')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Сбросить пароль')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повтор пароля',
                              validators=[DataRequired(),
                                          EqualTo('password')])
    submit = SubmitField('Сменить пароль')


class AddAdPostForm(FlaskForm):

    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired()])

    photo = FileField('Image',
                      validators=[
                          FileRequired(),
                          FileAllowed(['jpg', 'png', 'bmp'], 'Images only!')
                      ])

    price = IntegerField(validators=[DataRequired()])

    submit = SubmitField('Ok')


class AdPostEditForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Body', validators=[DataRequired()])
    category = QuerySelectField(
        query_factory=lambda: Category.query.all(),
        get_label='name',
        allow_blank=False,
        blank_text=(u'Select a role'),
        get_pk=lambda x: x.id,
        default=lambda: Category.get(current_user.id).one())
    price = IntegerField(validators=[DataRequired()])
    submit = SubmitField('Ok')
    cancel = SubmitField('Cancel')


class AdPostEditPhotoForm(FlaskForm):

    photo = FileField('Image',
                      validators=[
                          FileRequired(),
                          FileAllowed(['jpg', 'png', 'bmp'], 'Images only!')
                      ])

    submit = SubmitField('Изменить фото')


class AddCategoryForm(FlaskForm):

    category = StringField('Наименование категории',
                           validators=[DataRequired()])
    submit = SubmitField('Добавить')


class ServerContactsForm(FlaskForm):

    enterprise = StringField('Enterprise', render_kw={'disabled': 'disabled'})
    contact_string = TextAreaField('Контакты')
    desc = TextAreaField('Описание')
    workPlaceCount = IntegerField('Количество рабочих мест', default=0)
    password = StringField('Пароль к БД')
    submit = SubmitField('Изменить')

class ServerContactsHistoryForm(FlaskForm):
    event = StringField('Событие')
    submit = SubmitField('Добавить')

class AddContact(FlaskForm):
    department = QuerySelectField(query_factory=lambda: Department.query.all(),
                                  get_label='name',
                                  allow_blank=False,
                                  blank_text=(u'Select a role'),
                                  get_pk=lambda x: x.dep_id,
                                  default=lambda: Department.query.first())
    name = StringField('Контакт', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[DataRequired()])
    desc = TextAreaField('Описание')
    submit = SubmitField('Добавить')


class AddDepartment(FlaskForm):
    dept = StringField('Подразделение', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class EditContact(FlaskForm):
    department = QuerySelectField(query_factory=lambda: Department.query.all(),
                                  get_label='name',
                                  allow_blank=False,
                                  blank_text=(u'Select a role'),
                                  get_pk=lambda x: x.dep_id)
    name = StringField('Контакт', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[DataRequired()])
    desc = TextAreaField('Описание')
    submit = SubmitField('Изменить')
    cancel = SubmitField('Отменить')


class AddTask(FlaskForm):
    task_name = StringField('Задача', validators=[DataRequired()])
    task_description = TextAreaField('Описание задачи',
                                     validators=[DataRequired()],
                                     render_kw={
                                         "rows": 1,
                                         "cols": 20
                                     })

    task_executor = QuerySelectField(
        query_factory=lambda: User.query.all(),
        get_label='username',
        allow_blank=False,
        default=lambda: User.query.filter_by(id=current_user.id).first(),
        get_pk=lambda x: x.id)
    task_limitdate = DateField('Срок',
                               validators=[Required()],
                               default=datetime.today)
    submit = SubmitField('Добавить')


class TaskEditForm(FlaskForm):
    task_name = StringField('Задача', validators=[DataRequired()])
    task_description = TextAreaField('Описание задачи',
                                     validators=[DataRequired()],
                                     render_kw={
                                         "rows": 1,
                                         "cols": 20
                                     })
    task_execution_description = TextAreaField('Комментарий исполнения',
                                               render_kw={
                                                   "rows": 1,
                                                   "cols": 20
                                               })
    task_executor = QuerySelectField(
        query_factory=lambda: User.query.all(),
        get_label='username',
        allow_blank=False,
        default=lambda: User.query.filter_by(id=current_user.id).first(),
        get_pk=lambda x: x.id)
    task_limitdate = DateField('Срок',
                               validators=[Required()],
                               default=datetime.today)
    submit = SubmitField('Добавить')


class AddInstruction(FlaskForm):
    category = QuerySelectField(query_factory=lambda: Category.query.all(),
                                get_label='name',
                                allow_blank=True,
                                blank_text=('Select a role'),
                                get_pk=lambda x: x.id,
                                validators=[DataRequired()])
    theme = StringField('Тема', validators=[DataRequired()])
    
    trouble = CKEditorField('Инструкция',
                            validators=[DataRequired()])
    
    submit = SubmitField('Изменить')
    cancel = SubmitField('Отменить')


class SearchInsForm(FlaskForm):
    search = StringField('Поиск')
    submit = SubmitField('Поиск')

class EditInstruction(FlaskForm):
    category = QuerySelectField(query_factory=lambda: Category.query.all(),
                                get_label='name',
                                allow_blank=True,
                                blank_text=('Select a role'),
                                get_pk=lambda x: x.id,
                                validators=[DataRequired()]
                                )

    theme = StringField('Тема', validators=[DataRequired()])
    
    trouble = CKEditorField('Инструкция',
                            validators=[DataRequired()])
    
    submit = SubmitField('Изменить')
    cancel = SubmitField('Отменить')


class QueryPortalForm(FlaskForm):
    ip_form = StringField('Server IP')
    password_form = PasswordField('DB Password')
    dbname_form = StringField('Database name')
    query_form = TextAreaField('Query')
    result_form = TextAreaField('Result')

    submit = SubmitField('Submit')

class AddReportForm(FlaskForm):   
    report_body = TextAreaField('', validators=[DataRequired()])
    date = DateField(default=datetime.today)
    submit = SubmitField('Добавить')

class NewDNSubmit(FlaskForm):
    host_ip = StringField(label=None)
    password = StringField(label=None)
    user_id = StringField(label=None)
    # Изменить на TextAreaField и поменять на form.content(value )
    dnstring = StringField(label=None)
    submit = SubmitField('Изменить')