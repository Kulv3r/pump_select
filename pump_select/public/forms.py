# -*- coding: utf-8 -*-
"""Public forms."""
from flask_wtf import Form
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired


class CharacteristicValuesForm(Form):
    xx = StringField(validators=[DataRequired()])
    yy = PasswordField(validators=[DataRequired()])
