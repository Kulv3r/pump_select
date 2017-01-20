# -*- coding: utf-8 -*-
"""Application assets."""
from flask_assets import Bundle, Environment

css = Bundle(
    # 'libs/font-awesome/css/font-awesome.min.css',
    # 'libs/bootstrap/dist/css/bootstrap.min.css',
    'css/style.css',
    filters='cssmin',
    output='public/css/common.css'
)

js = Bundle(
    # 'libs/jQuery/dist/jquery.min.js',
    # 'libs/bootstrap/dist/js/bootstrap.min.js',
    # 'libs/highcharts/highcharts.js',
    'js/plugins.js',
    filters='jsmin',
    output='public/js/common.js'
)

assets = Environment()

assets.register('js_all', js)
assets.register('css_all', css)
