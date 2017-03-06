# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Regexp, Optional

from pump_select.general.constants import CurrentFrequencies, RPM
from pump_select.manufacturers.models import MotorManufacturer


class MotorForm(FlaskForm):
    manufacturer = QuerySelectField(
        'Manufacturer',
        query_factory=lambda: (
            MotorManufacturer.query
            .filter(MotorManufacturer.deleted_at.is_(None))
            .order_by(MotorManufacturer.name.asc())
        ),
        get_label=lambda m: m.name,
    )
    name = StringField('Name', validators=[InputRequired()])
    power = FloatField('Power, kW', validators=[InputRequired()])
    voltage = IntegerField('Voltage, V', validators=[InputRequired()])
    current_frequency = SelectField(
        'Current frequency, Hz',
        choices=CurrentFrequencies.ALL_AS_OPTIONS,
        coerce=int,
    )
    rpm = SelectField(
        'RPM',
        choices=RPM.ALL_AS_OPTIONS,
        coerce=int,
    )
    _ip_protection = StringField(
        'Body protection, "IP-??"',
        validators=[(Regexp('[1-9][1-9]')), Optional()],
    )
    explosion_protected = BooleanField('Protected from explosion?')
    mass = IntegerField('Mass, kg', validators=[InputRequired()])
