# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, StringField, BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import Optional, InputRequired

from pump_select.general.constants import RPM
from pump_select.manufacturers.models import PumpManufacturer
from pump_select.pumps.constants import PumpCategory, SealTypes
from pump_select.pumps.fields import CSVField


class PumpForm(FlaskForm):
    manufacturer = QuerySelectField(
        query_factory=lambda: (
            PumpManufacturer.query
            .filter(PumpManufacturer.deleted_at.is_(None))
            .order_by(PumpManufacturer.name.asc())
        ),
        get_label=lambda m: m.name,
    )
    category = SelectField(
        choices=PumpCategory.ALL_AS_OPTIONS,
        coerce=int,
    )
    name = StringField('Series title', validators=[InputRequired()])
    size_type = StringField('Dimension-type', validators=[InputRequired()])
    inbound_diameter = FloatField()
    inbound_pressure = FloatField()
    outbound_diameter = FloatField()
    outbound_pressure = FloatField()
    seal_type = SelectField(
        choices=SealTypes.ALL_AS_OPTIONS,
        coerce=int,
    )
    mass = IntegerField()
    max_pressure = FloatField()
    frequency_regulation_needed = BooleanField()
    fluid_temp_min = IntegerField()
    fluid_temp_max = IntegerField()


class CharacteristicValuesForm(FlaskForm):
    # Input values
    H = CSVField(u'H, <br/>m')
    Q_H = CSVField(u'Q, <br/>m3/h')
    EFF = CSVField(u'Efficiency, <br/>%')
    Q_EFF = CSVField(u'Q, <br/>m3/h')
    PWR = CSVField(u'Power, <br/>kW')
    Q_PWR = CSVField(u'Q, <br/>m3/h')
    NPSHr = CSVField(u'NPSHr, <br/>m')
    Q_NPSHr = CSVField(u'Q, <br/>m3/h')

    # Q/H/Efficiency correction point
    Qcor = FloatField(u'Optimal Q', validators=[Optional()])
    Hcor = FloatField(u'Optimal H', validators=[Optional()])
    EFFcor = FloatField(u'Optimal Eff.', validators=[Optional()])

    # Polynom powers
    H_Q_polynom_n = SelectField(
        u'H(Q)',
        choices=[(i, str(i)) for i in range(3, 9)],
        coerce=int,
        default=4,
    )
    EFF_Q_polynom_n = SelectField(
        u'Eff.(Q)',
        choices=[(i, str(i)) for i in range(3, 9)],
        coerce=int,
        default=4,
    )
    PWR_Q_polynom_n = SelectField(
        u'Power(Q)',
        choices=[(i, str(i)) for i in range(3, 9)],
        coerce=int,
        default=4,
    )
    NPSHr_Q_polynom_n = SelectField(
        u'NPSHr(Q)',
        choices=[(i, str(i)) for i in range(3, 9)],
        coerce=int,
        default=3,
    )

    # Engine Revolutions per minute
    rpm_preset_other_option = 0, u'other...'
    rpm_preset = SelectField(
        u'RPM',
        choices=RPM.ALL_AS_OPTIONS + [rpm_preset_other_option],
        coerce=int,
        default=RPM.RPM_1500,
    )
    # `rpm_custom` is shown only if 'rpm_preset_other_option' is selected in `rpm_preset`.
    rpm_custom = IntegerField(u'Custom RPM:', validators=[Optional()])

    # Q application range
    Qmin = IntegerField(u'Q min, m3', validators=[Optional()])
    Qmax = IntegerField(u'Q max, m3', validators=[Optional()])

    def populate_from_obj(self, obj):
        # Fill the form with the data from object, for example default data, or corrected pump data.
        for attr in ('H', 'Q_H', 'EFF', 'Q_EFF', 'NPSHr', 'Q_NPSHr'):
            field = getattr(self, attr)
            field.data = [round(i, 2) for i in getattr(obj, attr)]

        # self._Qmin.data = obj.Qmin
        # self._Qmax.data = obj.Qmax
