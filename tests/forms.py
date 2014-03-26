from wtforms import Form, TextField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length
from wtforms_alchemy import ModelForm

from tests.models import Author


class AuthorForm(ModelForm):
    class Meta:
        model = Author
        include = ['name', 'slug']


class ContactForm(Form):
    name = TextField(validators=[DataRequired(), Length(max=100)])
    message = TextAreaField()
