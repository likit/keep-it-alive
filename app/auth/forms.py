from flask_wtf import FlaskForm
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, EqualTo
from wtforms_alchemy import model_form_factory

from app import db
from app.auth.models import User

BaseModelForm = model_form_factory(FlaskForm)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class LoginForm(ModelForm):
    class Meta:
        model = User
        unique_validator = None

    password = PasswordField('Password', validators=[DataRequired()])
