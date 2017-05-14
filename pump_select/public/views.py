# -*- coding: utf-8 -*-
from flask import Blueprint, flash, render_template

from pump_select import example_data
from pump_select.pumps.forms import CharacteristicValuesForm
from pump_select.pumps.models import PumpCharacteristic
from pump_select.utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder='../static')


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    return render_template('public/home.html')


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html')
