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
