# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea

from pump_select.validators import CSVCoercible


class CharacteristicValuesForm(FlaskForm):
    x_csv = StringField(
        u'Axis "X" values',
        widget=TextArea(),
        validators=[DataRequired(), CSVCoercible(float)],
    )
    y_csv = StringField(
        u'Axis "Y" values',
        widget=TextArea(),
        validators=[DataRequired(), CSVCoercible(float)],
    )
