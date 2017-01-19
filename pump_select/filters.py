# -*- coding: utf-8 -*-
"""
Define your custom template filters here.
Dont forget to register it in app.py file.

All the filters should have a postfix "_filter" so they can be used in the python code also.
Registered filter should be named the same except for no postfix.
"""


def datetime_filter(dt):
    return dt.strftime('%d.%m.%y at %H:%M')
