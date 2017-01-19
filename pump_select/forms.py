from flask_wtf import Form


class InsecureForm(Form):
    """
    Is useful for included forms via field_lists + form_fields.
    """
    def __init__(self, *args, **kwargs):
        self.csrf_enabled = False
        super(InsecureForm, self).__init__(*args, **kwargs)
