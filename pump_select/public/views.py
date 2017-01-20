# -*- coding: utf-8 -*-
import numpy as np
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from pump_select import data
from pump_select.extensions import login_manager
from pump_select.public.forms import CharacteristicValuesForm
from pump_select.user.forms import RegisterForm, LoginForm
from pump_select.user.models import User
from pump_select.utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder='../static')


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    Q, H = data.Q1, data.H1

    form = CharacteristicValuesForm()

    if request.method == 'GET':
        form.x_csv.data = Q
        form.y_csv.data = H

    if form.validate_on_submit():
        Q = form.x_csv.data
        H = form.y_csv.data

    elif request.method == 'POST':
        flash_errors(form)

    points_series_data = [list(i) for i in zip(Q, H)]

    polynoms_vals = {}
    for n in (2, 4, 6, 8):
        polynom = np.polynomial.polynomial.polyfit(Q, H, n)

        min_x = Q[0]
        max_x = Q[-1]
        if max_x < min_x:
            min_x, max_x = max_x, min_x
        steps = len(Q)*10
        step = round((max_x - min_x) / steps, 1)

        x_vals = [min_x + step*i for i in xrange(steps+1)]
        x_series = [round(i, 2) for i in
                    np.polynomial.polynomial.polyval(x_vals, polynom).tolist()]

        polynoms_vals[n] = [list(i) for i in zip(x_vals, x_series)]

    form.x_csv.data = '\n'.join([str(i) for i in form.x_csv.data])
    form.y_csv.data = '\n'.join([str(i) for i in form.y_csv.data])

    return render_template(
        'public/home.html',
        form=form,
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
