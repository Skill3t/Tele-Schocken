from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextField
from wtforms.validators import DataRequired, Length, Optional, Email
from wtforms.fields.html5 import EmailField

BROWSER = (
        'Chrome',
        'Safari',
        'Edge',
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


class FeedbackFrom(FlaskForm):
    message = TextField('Nachricht', validators=[Length(min=0, max=450), DataRequired()])
    browser = SelectField(label='Browser', choices=[(browser, browser) for browser in BROWSER], validators=[DataRequired()], default='Chrome')
    mail = EmailField('E-Mai Adresse für Rückfragen (Optional)', validators=[Optional(), Email()])
