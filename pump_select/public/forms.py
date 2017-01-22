# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class CSVField(StringField):
    widget = TextArea()

    def __init__(self, label=None, coerse_func=None, delimiter=None, *args, **kwargs):
        self.coerse_func = coerse_func or str
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
    Q_H = CSVField(
        u'"Q" values, m3/h',
        coerse_func=float,
    )
    H = CSVField(
        u'"H" values, m',
        coerse_func=float,
    )
    Q_eff = CSVField(
        u'"Q" values, m3/h',
        coerse_func=float,
    )
    eff = CSVField(
        u'"Efficiency" values, %%',
        coerse_func=float,
    )
    Q_NPSHr = CSVField(
        u'"Q" values, m3/h',
        coerse_func=float,
    )
    NPSHr = CSVField(
        u'"NPSHr" values, ??',
        coerse_func=float,
    )
