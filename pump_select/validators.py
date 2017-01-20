from wtforms import ValidationError


class Unique(object):
    """ validator that checks field uniqueness """
    def __init__(self, model, field, message=None):
        self.model = model
        self.field = getattr(model, field)
        self.message = message or u'This element already exists.'

    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()

        id = form.id.data if 'id' in form else None

        if check and (id is None or id != check.id):
            raise ValidationError(self.message)


class CSVCoercible(object):
    """ validator that checks field can be coerced to smth from a CSV"""
    def __init__(self, coerse_func, delimiter=None, message=None):
        self.coerse_func = coerse_func
        self.delimiter = delimiter
        self.message = message or u'CSV format error.'.format(self.delimiter)

    def __call__(self, form, field):
        data = field.data.strip()

        self.detect_delimiter(data)

        try:
            values = [self.coerse_func(val) for val in data.split(self.delimiter)]
        except Exception:
            raise ValidationError(self.message)

        field.data = values

    def detect_delimiter(self, data):
        if self.delimiter is not None:
            return self.delimiter

        possible_delimiters = [' ', ',', ';', '\n', '\n\r', '\t']
        delimiter_used_times = []
        for delimiter in possible_delimiters:
            delimiter_used_times.append((data.count(delimiter), delimiter))

        self.delimiter = max(delimiter_used_times)[1]
        print('delimiter is:', self.delimiter)
        print(data)
