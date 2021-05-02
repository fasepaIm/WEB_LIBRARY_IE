from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class UploadBookForm(FlaskForm):
    bookname = StringField('Название книги:', validators=[DataRequired()])
    author = StringField('Автор книги:', validators=[DataRequired()])
    description = TextAreaField('Описание книги:', validators=[DataRequired()])
    reading_time = StringField('Примерное время прочтения:', validators=[DataRequired()])
    cover_image = FileField('Обложка книги:', validators=[FileRequired()])
    book_file = FileField('Файл книги:', validators=[FileRequired()])
    submit = SubmitField('Добавить книгу')
