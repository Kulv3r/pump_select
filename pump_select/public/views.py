# -*- coding: utf-8 -*-
from numpy.polynomial import polynomial as P
from scipy.optimize import minimize_scalar
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from pump_select import data
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
    x_series = [round(i, 2) for i in P.polyval(x_vals, polynom).tolist()]
    return [list(i) for i in zip(x_vals, x_series)]


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    form = CharacteristicValuesForm()

    # Fill the form with the default example data
    if request.method == 'GET':
        for attr in ('H', 'Q_H', 'eff', 'Q_eff', 'NPSHr', 'Q_NPSHr'):
            field = getattr(form, attr)
            field.data = getattr(data, attr)

    if not form.validate_on_submit():
        flash_errors(form)

    # Calculate polynomes based on the points given
    polynoms = []
    polynom_vals = []
    points = []
    for x, y, n in (
            (form.Q_H.data, form.H.data, form.H_Q_polynom_n.data),
            (form.Q_eff.data, form.eff.data, form.eff_Q_polynom_n.data),
            (form.Q_NPSHr.data, form.NPSHr.data, form.NPSHr_Q_polynom_n.data),
    ):
        polynom = P.polyfit(x, y, n)
        polynoms.append(polynom)

        vals = polyvals(polynom, limits=[0, 1000])
        polynom_vals.append(vals)

        # Also convert points to chart series
        points.append(data.list_zip(x, y))

    chart_data = [
        {
            'name': 'H(Q)',
            'data': polynom_vals[0],
            'suffix': 'm',
            'valueDecimals': 0,
            'points': points[0],
        },
        {
            'name': 'Efficiency(Q)',
            'data': polynom_vals[1],
            'suffix': '%',
            'valueDecimals': 1,
            'points': points[1],
        },
        {
            'name': 'NPSHr(Q)',
            'data': polynom_vals[2],
            'suffix': 'm',
            'valueDecimals': 2,
            'points': points[2],
        },
    ]

    H_Q_polynom, eff_Q_polynom, NPSHr_Q_polynom = polynoms

    # Get max efficiency
    poly_der = P.polyder(eff_Q_polynom)  # Differentiate a polynomial.
    roots = P.polyroots(poly_der)  # Compute the roots of a polynomial.
    real_roots = [r.real for r in roots if not r.imag]
    if len(real_roots) != 1:
        flash(u'Invalid real roots for Eff.(Q) function: {}. '
              u'Should be only 1 real root.'.format(real_roots),
              category='danger')
    else:
        Qnom = real_roots[0]
        eff_max = P.polyval(Qnom, eff_Q_polynom)
        Hnom = P.polyval(Qnom, H_Q_polynom)
        flash(u'Qnom={Qnom} &nbsp;&nbsp;&nbsp; '
              u'Hnom={Hnom} &nbsp;&nbsp;&nbsp; '
              u'Eff_max={eff_max}'.format(**locals()),
              category='success')

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
