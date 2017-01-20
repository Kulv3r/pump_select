# -*- coding: utf-8 -*-
import numpy as np
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from pump_select import data
from pump_select.extensions import login_manager
from pump_select.user.forms import RegisterForm, LoginForm
from pump_select.user.models import User
from pump_select.utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder='../static')


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    points_series_data = [list(i) for i in zip(data.Q1, data.H1)]

    # form = CharacteristicValuesForm()
    # if form.validate_on_submit():
    #     1
    # elif request.method == 'POST':
    #     flash_errors(form)

    polynoms_vals = {}
    for n in (2, 4, 6):
        polynom = np.polynomial.polynomial.polyfit(data.Q1, data.H1, n)

        min_x = data.Q1[0]
        max_x = data.Q1[-1]
        if max_x < min_x:
            min_x, max_x = max_x, min_x
        steps = 50
        step = (max_x - min_x) / steps

        x_vals = [min_x + step*i for i in xrange(steps)]
        x_series = np.polynomial.polynomial.polyval(x_vals, polynom).tolist()

        polynoms_vals[n] = [list(i) for i in zip(x_vals, x_series)]

    return render_template(
        'public/home.html',
        # form=form,
        points_series_data=points_series_data,
        polynoms_vals=polynoms_vals,
    )


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
    form = LoginForm(request.form)
    return render_template('public/about.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))
