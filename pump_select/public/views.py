# -*- coding: utf-8 -*-
import numpy as np
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from pump_select.data import *
from pump_select.extensions import login_manager
from pump_select.loggers import logger
from pump_select.public.forms import CharacteristicValuesForm
from pump_select.user.forms import RegisterForm, LoginForm
from pump_select.user.models import User
from pump_select.utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder='../static')


def polyvals(polynom, limits, steps=100):
    min_x, max_x = limits
    if max_x < min_x:
        min_x, max_x = max_x, min_x
    step = round((max_x - min_x) / steps, 1)

    x_vals = [min_x + step * i for i in range(steps + 1)]
    x_series = [round(i, 2) for i in
                np.polynomial.polynomial.polyval(x_vals, polynom).tolist()]
    return [list(i) for i in zip(x_vals, x_series)]


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    form = CharacteristicValuesForm()

    if request.method == 'GET':
        form.H.data = H
        form.Q_H.data = Q_H
        form.eff.data = eff
        form.Q_eff.data = Q_eff
        form.NPSHr.data = NPSHr
        form.Q_NPSHr.data = Q_NPSHr

    if not form.validate_on_submit():
        flash_errors(form)

    polynom_vals = []
    for x, y, n in (
            (form.Q_H.data, form.H.data, form.polynom_n.data),
            (form.Q_eff.data, form.eff.data, form.polynom_n.data),
            (form.Q_NPSHr.data, form.NPSHr.data, form.polynom_n.data),
    ):
        polynom = np.polynomial.polynomial.polyfit(x, y, n)
        vals = polyvals(polynom, limits=[0, 1000])
        polynom_vals.append(vals)

    chart_data = [
        {
            'name': 'H(Q)',
            'data': polynom_vals[0],
            'valueDecimals': 0,
            'points': H_Q,
        },
        {
            'name': 'Efficiency(Q)',
            'data': polynom_vals[1],
            'valueDecimals': 1,
            'points': eff_Q,
        },
        {
            'name': 'NPSHr(Q)',
            'data': polynom_vals[2],
            'valueDecimals': 2,
            'points': NPSHr_Q,
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
