# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
import os
import string
from random import SystemRandom

from flask import flash
from sqlalchemy.util import classproperty
from sqlalchemy_utils import Choice


def flash_errors(form, category='warning'):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash('{0} - {1}'.format(getattr(form, field).label.text, error), category)


def get_env_or_fail(key):
    """
    Get the specified environment variable or fail with error if it's missing.
    Why? To avoid silent misconfiguration errors for required env variables.
    :raises: ConfigError
    """
    val = os.environ.get(key)
    if not val:
        raise Exception('Missing env var: {}'.format(key))
    return val


def generate_random_code(length=12):
    return ''.join(SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(length))


def constants_dict(constants_module):
    constant_names = [i for i in dir(constants_module) if i[0].isupper()]
    shared_constants = [getattr(constants_module, name) for name in constant_names]
    return dict([(i.__name__, i) for i in shared_constants if hasattr(i, '__name__')])


class Constant(object):
    """
    Base class for constants.
    Supposed you have several constants, which defined like this:

    RED = 1  <-- a code, that will be saved to DB
    GREEN = 2
    BLUE = 3

    And a user-friendly representation as a dict:
    repr = {
        RED: u'Red color',
        GREEN: u'Good color',
        BLUE: u'Blue dabudee dabudaay',
    }
    """
    @classmethod
    def choice(cls, code):
        return Choice(code, cls.repr[code])

    @classproperty
    def ALL_(cls):
        uppercase_attrs = [i for i in cls.__dict__.keys() if i.isupper()]
        unsorted_attrs = [getattr(cls, i) for i in uppercase_attrs]
        return sorted(unsorted_attrs)

    @classproperty
    def ALL_AS_OPTIONS(cls):
        return [(i, cls.repr[i]) for i in cls.ALL_]
