from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CreateGameFrom(FlaskForm):
    adminname = StringField('Name', validators=[Length(min=0, max=450), DataRequired()])
    save = SubmitField('Erzeugen')
