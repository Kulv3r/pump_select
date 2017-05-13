# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired


class PumpManufacturerForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])


class MotorManufacturerForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
