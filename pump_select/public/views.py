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
    H = np.array(data.H1)
    Q = np.array(data.Q1)

    points_series_data = [(q, data.H1[idx]) for idx, q in enumerate(data.Q1)]

    polynoms = {}
    polynoms_vals = {}
    for n in (2, 4, 6):
        polynom = np.polynomial.polynomial.polyfit(Q, H, n).tolist()
        # It returns for an n=4
        # [1.16035322e+02, -6.77159076e-04, 7.49052572e-06, -7.71847069e-08, 3.72781671e-11]
        #       A                 B                 C              D               E
        # so formula = A + Bx + Cx**2 + Dx**3 + Ex**4
        x = data.Q1[0]
        max_x = data.Q1[-1]
        if max_x < x:
            x, max_x = max_x, x
        steps = len(data.Q1)
        step = (max_x - x) / steps
        series = []
        while x < max_x:
            # f = p[0] + p[1] * x**1 + p[2] * x**2 + ...
            f = sum([(c * x**p) for p, c in enumerate(polynom)])
            series.append((round(x, 1), round(f, 1)))
            x += step

        polynoms_vals[n] = series

    # form = CharacteristicValuesForm()
    # if form.validate_on_submit():
    #     1
    # elif request.method == 'POST':
    #     flash_errors(form)

    return render_template(
        'public/home.html',
        # form=form,
        polynoms_vals=polynoms_vals,
        points_series_data=points_series_data,
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
