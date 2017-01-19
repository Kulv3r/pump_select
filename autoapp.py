# -*- coding: utf-8 -*-
"""Create an application instance."""
from pump_select.app import create_app
from pump_select.settings import config


app = create_app(config)
