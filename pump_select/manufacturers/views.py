# -*- coding: utf-8 -*-
import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for

from pump_select.extensions import db
from pump_select.manufacturers.forms import PumpManufacturerForm, MotorManufacturerForm
from pump_select.manufacturers.models import PumpManufacturer, MotorManufacturer
from pump_select.utils import flash_errors

blueprint = Blueprint('manufacturers', __name__, url_prefix='/manufacturers', static_folder='../static')


manufacturer_type_map = {
    'pump': (PumpManufacturer, PumpManufacturerForm),
    'motor': (MotorManufacturer, MotorManufacturerForm),
}


@blueprint.route('/<manufacturer_type>')
def all_(manufacturer_type):
    Model, Form = manufacturer_type_map[manufacturer_type]

    manufacturers = Model.query.order_by(Model.name.asc()).all()

    return render_template('manufacturers/list.html', **locals())


@blueprint.route('/add/<manufacturer_type>', methods=['GET', 'POST'])
@blueprint.route('/edit/<manufacturer_type>/<int:manufacturer_id>', methods=['GET', 'POST'])
def edit(manufacturer_type, manufacturer_id=None):
    Model, Form = manufacturer_type_map[manufacturer_type]

    manufacturer = Model()
    if manufacturer_id:
        manufacturer = Model.query.get_or_404(manufacturer_id)

    form = Form(obj=manufacturer)

    if form.validate_on_submit():
        form.populate_obj(manufacturer)

        if not manufacturer_id:
            db.session.add(manufacturer)

        db.session.commit()
        flash('Saved.', category='success')
        return redirect(url_for('.all_', manufacturer_type=manufacturer_type))

    return render_template('manufacturers/edit.html', **locals())


@blueprint.route('/delete/<manufacturer_type>/<int:manufacturer_id>')
def delete(manufacturer_type, manufacturer_id):
    Model, Form = manufacturer_type_map[manufacturer_type]

    manufacturer = Model.query.get_or_404(manufacturer_id)
    if manufacturer.deleted_at:
        manufacturer.deleted_at = None
    else:
        manufacturer.deleted_at = datetime.datetime.utcnow()

    db.session.commit()
    flash('Saved.', category='success')
    return redirect(request.referrer)
