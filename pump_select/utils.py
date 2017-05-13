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


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class Constant(object):
    """
    Base class for constants.
    Supposed you have several constants, which defined like this:

    FREELANCER = 1  <-- a code, that will be saved to DB
    AGENCY = 2
    GROUP = 3
    COMPANY = 4

    And a user-friendly representation as a dict:
    labels = {
        FREELANCER: 'Freelancer',
        AGENCY: 'Agency',
        GROUP: 'Group',
        COMPANY: 'Company',
    }

    To use this constant as a choice field, define a DB field like this:
        my_field = Column(ChoiceType(choices=MyConstantsClass.ALL_AS_OPTIONS, impl=db.Integer()))
    """
    labels = {}

    _all = None
    _all_as_options = None

    @classproperty
    def ALL(cls):
        """
        :return: A list of ALL constants in this class,
        i.e. [1, 2, 3, 4].
        Uppercase attrs only.
        Redefine it, if you need a custom order.
        """
        if not cls._all:
            cls._all = [value for name, value in cls.__dict__.items()
                        if name.isupper() and not name.startswith(('ALL', 'OPTIONS'))]
        return cls._all

    @classproperty
    def OPTIONS(cls):
        """
        :return: A list of 2-tuples options, 
        i.e. [
            (1, 'Freelancer'),
            (2, 'Agency'),
            (3, 'Group'),
            (4, 'Company'),
        ]
        Needs a "cls.labels" dict with labels to be defined.
        """
        if not cls._all_as_options:
            cls._all_as_options = [(i, cls.labels.get(i, i)) for i in cls.ALL]
        return cls._all_as_options

    @classmethod
    def choice(cls, code):
        """ Get a <Choice> instance from its code. """
        return Choice(code, cls.labels[code])
