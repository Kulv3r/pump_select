# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, HiddenField, FloatField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import Optional
from wtforms.widgets import TextArea
from wtforms_components import read_only

from pump_select.public.constants import RPM


class CSVField(StringField):
    widget = TextArea()

    def __init__(self, label=None, coerse_func=float, delimiter=None, *args, **kwargs):
        self.coerse_func = coerse_func
        self.delimiter = delimiter

        super(StringField, self).__init__(label, *args, **kwargs)

    def _value(self):
        if type(self.data) is list:
            return '\n'.join([str(i) for i in self.data])
        return ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = self.coerce_to_list(valuelist[0])
        else:
            self.data = ''

    def coerce_to_list(self, string_val):
        data = string_val.strip()
        if not data:
            return

        self.detect_delimiter(data)

        values = [self.coerse_func(val) for val in data.split(self.delimiter)]

        return values

    def detect_delimiter(self, data):
        if self.delimiter is not None:
            return

        possible_delimiters = ' ', ',', ';', '\r\n', '\n', '\t'

        delimiter_used_times = []
        for delimiter in possible_delimiters:
            delimiter_used_times.append((data.count(delimiter), delimiter))

        delimiter_used_times.sort()

        # Delimiter must be present in the data N-1 times, where N - number of items.
        for delimiter_count, delimiter in delimiter_used_times:
            if not delimiter_count:
                continue
            items = data.split(delimiter)
            is_valid_delimiter = len(items) - delimiter_count == 1
            if is_valid_delimiter:
                self.delimiter = delimiter
                return

        raise Exception(u'Cant detect delimiter.')


class CharacteristicValuesForm(FlaskForm):
    H = CSVField(u'H, <br/>m')
    Q_H = CSVField(u'Q, <br/>m3/h')
    EFF = CSVField(u'Efficiency, <br/>%')
    Q_EFF = CSVField(u'Q, <br/>m3/h')
    NPSHr = CSVField(u'NPSHr, <br/>m')
    Q_NPSHr = CSVField(u'Q, <br/>m3/h')

    Qcor = FloatField(u'Optimal Q', validators=[Optional()])
    Hcor = FloatField(u'Optimal H', validators=[Optional()])
    EFFcor = FloatField(u'Optimal Eff.', validators=[Optional()])

    H_Q_polynom_n = SelectField(
        u'H(Q) polynom power',
        choices=[(i, str(i)) for i in range(3, 9)],
        coerce=int,
        default=4,
    )
    EFF_Q_polynom_n = SelectField(
        u'Eff.(Q) polynom power',
        choices=[(i, str(i)) for i in range(3, 9)],
        coerce=int,
        default=4,
    )
    NPSHr_Q_polynom_n = SelectField(
        u'NPSHr(Q) polynom p-r',
        choices=[(i, str(i)) for i in range(3, 9)],
        coerce=int,
        default=3,
    )
    rpm_preset_other_option = 0, u'other...'
    rpm_preset = SelectField(
        u'RPM',
        choices=RPM.ALL_AS_OPTIONS + [rpm_preset_other_option],
        coerce=int,
        default=RPM.RPM_1500,
    )
    # `rpm_custom` is shown only if 'rpm_preset_other_option' is selected in `rpm_preset`.
    rpm_custom = IntegerField(u'Custom RPM:', validators=[Optional()])
    ns = IntegerField(u'Resulting ns', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        read_only(self.ns)

    def populate_from_obj(self, obj):
        # Fill the form with the data from object, for example default data, or corrected pump data.
        for attr in ('H', 'Q_H', 'EFF', 'Q_EFF', 'NPSHr', 'Q_NPSHr'):
            field = getattr(self, attr)
            field.data = [round(i, 2) for i in getattr(obj, attr)]
