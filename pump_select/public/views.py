# -*- coding: utf-8 -*-
from numpy.polynomial import polynomial as P
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, logout_user

from pump_select import data
from pump_select.extensions import login_manager
from pump_select.loggers import logger
from pump_select.public.constants import *
from pump_select.public.forms import CharacteristicValuesForm
from pump_select.public.models import Pump
from pump_select.user.forms import RegisterForm
from pump_select.user.models import User
from pump_select.utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder='../static')


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    form = CharacteristicValuesForm()

    if form.is_submitted():
        if not form.validate():
            flash_errors(form)
    else:
        # Fill the form with the default example data
        for attr in ('H', 'Q_H', 'EFF', 'Q_EFF', 'NPSHr', 'Q_NPSHr'):
            field = getattr(form, attr)
            field.data = getattr(data, attr)

    pump = Pump()
    form.populate_obj(pump)
    pump.get_bep()

    chart_data = [
        {
            'name': 'H(Q)',
            'data': pump.polynom('H(Q)').vals(),
            'suffix': 'm',
            'valueDecimals': 0,
            'points': pump.polynom('H(Q)').points(),
        },
        {
            'name': 'Efficiency(Q)',
            'data': pump.polynom('EFF(Q)').vals(),
            'suffix': '%',
            'valueDecimals': 1,
            'points': pump.polynom('EFF(Q)').points(),
        },
        {
            'name': 'NPSHr(Q)',
            'data': pump.polynom('NPSHr(Q)').vals(),
            'suffix': 'm',
            'valueDecimals': 2,
            'points': pump.polynom('NPSHr(Q)').points(),
        },
    ]

    return render_template('public/home.html', **locals())


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """Register new user."""
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        User.create(username=form.username.data, email=form.email.data, password=form.password.data, active=True)
        flash('Thank you for registering. You can now log in.', 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))
