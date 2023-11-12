from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional

BROWSER = (
        'Chrome',
        'Safari',
        'Firefox',
        'Edge',
        'Opera',
        'Internet Explorer',
        'Sonstiger Android',
        'Sonstiger'
    )


class CreateGameFrom(FlaskForm):
    adminname = StringField('Name', validators=[Length(min=0, max=450), DataRequired()])
    save = SubmitField('Erzeugen')
