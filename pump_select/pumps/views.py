# -*- coding: utf-8 -*-
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, logout_user

from pump_select import example_data
from pump_select.extensions import login_manager
from pump_select.pumps.forms import CharacteristicValuesForm
from pump_select.pumps.models import PumpCharacteristic
from pump_select.users.forms import RegisterForm
from pump_select.users.models import User
from pump_select.utils import flash_errors

blueprint = Blueprint('pumps', __name__, static_folder='../static')


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    form = CharacteristicValuesForm()

    if form.is_submitted():
        if not form.validate():
            flash_errors(form)
    else:
        form.populate_from_obj(example_data)

    pump = PumpCharacteristic()
    form.populate_obj(pump)
    pump.calculate_missing()

    bep_exists = pump.get_bep()
    if not bep_exists:
        flash('Bad input data - Best Efficiency Point could not be found.', category='danger')
    else:
        correction_values = form.Qcor.data, form.Hcor.data, form.EFFcor.data
        if all(correction_values):
            flash(u'Corrected PumpCharacteristic data:', category='success')
            pump.correct(*correction_values)
            form.populate_from_obj(pump)

    return render_template('public/home.html', **locals())


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('.home'))


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """Register new user."""
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        User.create(username=form.username.data, email=form.email.data, password=form.password.data, active=True)
        flash('Thank you for registering. You can now log in.', 'success')
        return redirect(url_for('.home'))
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
