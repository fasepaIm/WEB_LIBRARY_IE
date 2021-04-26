from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class UploadBookForm(FlaskForm):
    bookname = StringField('Название книги:', validators=[DataRequired()])
    author = StringField('Автор книги:', validators=[DataRequired()])
    description = TextAreaField('Описание книги:', validators=[DataRequired()])
    reading_time = StringField('Примерное время прочтения:', validators=[DataRequired()])
    cover_image = FileField('Обложка книги:', validators=[DataRequired()])
    book_file = FileField('Файл книги:', validators=[DataRequired()])
    submit = SubmitField('Добавить книгу')
