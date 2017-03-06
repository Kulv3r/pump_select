# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for

from pump_select.extensions import db
from pump_select.motors.forms import MotorForm
from pump_select.motors.models import Motor

blueprint = Blueprint('motors', __name__, url_prefix='/motors', static_folder='../static')


@blueprint.route('/')
def all_():
    motors = Motor.query.order_by(Motor.name.asc()).all()
    return render_template('motors/list.html', **locals())


@blueprint.route('/add', methods=['GET', 'POST'])
@blueprint.route('/edit/<int:motor_id>', methods=['GET', 'POST'])
def edit(motor_id=None):
    if motor_id:
        motor = Motor.query.get_or_404(motor_id)
    else:
        motor = Motor()

    form = MotorForm(obj=motor)

    if form.validate_on_submit():
        form.populate_obj(motor)

        if not motor_id:
            db.session.add(motor)

        db.session.commit()
        flash('Saved.', category='success')
        return redirect(url_for('.all_'))

    return render_template('motors/edit.html', **locals())


@blueprint.route('/delete/<int:motor_id>')
def delete(motor_id):
    motor = Motor.query.get_or_404(motor_id)
    if motor.deleted_at:
        motor.deleted_at = None
    else:
        motor.deleted_at = datetime.datetime.utcnow()

    db.session.commit()
    flash('Saved.', category='success')
    return redirect(request.referrer)
