from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory

from app.tracker.models import *

BaseModelForm = model_form_factory(FlaskForm)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class ActivityForm(ModelForm):
    class Meta:
        model = TrackerActivity
        datetime_format = '%d/%m/%Y %H:%M'


class TaskForm(ModelForm):
    class Meta:
        model = TrackerTask
