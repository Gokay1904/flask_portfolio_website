from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField



##WTForm
class CreateDataPostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    img_url = StringField("Main Post Image", validators=[DataRequired(), URL()])
    body = CKEditorField("Data Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class LoginForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("Submit Post")



class ContactForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    message = StringField("message", validators=[DataRequired()])
    submit = SubmitField("Send Message")



class CreatePostForm(FlaskForm):
    title = StringField("Post Title", validators=[DataRequired()])
    subtitle = StringField("Post Subtitle", validators=[DataRequired()])
    img_url = StringField("Main Post Image", validators=[DataRequired(), URL()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    body = CKEditorField("body")
    submit = SubmitField("Login")
