# -*- coding: utf-8 -*-
from pprint import pprint

import datetime
from flask import Blueprint, flash, render_template, redirect, url_for, request

from pump_select import example_data
from pump_select.extensions import db
from pump_select.pumps.forms import CharacteristicValuesForm, PumpForm
from pump_select.pumps.models import PumpCharacteristic, Pump
from pump_select.utils import flash_errors

blueprint = Blueprint('pumps', __name__, static_folder='../static')


@blueprint.route('/pump/<int:pump_id>/')
def pump(pump_id):
    p = Pump.query.get_or_404(pump_id)
    return render_template('pumps/pump.html', pump=p)


@blueprint.route('/pumps/')
def pumps():
    all_pumps = Pump.query.order_by(Pump.manufacturer_id.asc(), Pump.name.asc())
    return render_template('pumps/list_pumps.html', pumps=all_pumps)


@blueprint.route('/add_pump/', methods=['GET', 'POST'])
@blueprint.route('/edit_pump/<int:pump_id>/', methods=['GET', 'POST'])
def edit_pump(pump_id=None):
    if pump_id:
        pump = Pump.query.get_or_404(pump_id)
    else:
        pump = Pump()

    form = PumpForm(obj=pump)

    if form.validate_on_submit():
        form.populate_obj(pump)

        if not pump_id:
            db.session.add(pump)

        db.session.commit()
        flash('Saved.', category='success')
        return redirect(url_for('pumps.pumps'))

    return render_template('motors/edit.html', **locals())


@blueprint.route('/delete_pump/<int:pump_id>/')
def delete_pump(pump_id):
    pump = Pump.query.get_or_404(pump_id)
    if pump.deleted_at:
        pump.deleted_at = None
    else:
        pump.deleted_at = datetime.datetime.utcnow()

    db.session.commit()
    flash('Saved.', category='success')
    return redirect(request.referrer)


@blueprint.route('/pump/<int:pump_id>/add_characteristic/', methods=['GET', 'POST'])
# @blueprint.route('/pump/<int:pump_id>/edit_characteristic/<int:char_id>/', methods=['GET', 'POST'])  # tbd
def edit_pump_characteristic(pump_id, char_id=None):
    form = CharacteristicValuesForm()

    if form.is_submitted():
        if not form.validate():
            flash_errors(form)
    else:
        form.populate_from_obj(example_data)

    pump_char = PumpCharacteristic()
    form.populate_obj(pump_char)
    pump_char.calculate_missing()

    bep_exists = pump_char.get_bep()
    if not bep_exists:
        flash('Bad input data - Best Efficiency Point could not be found.', category='danger')

    else:
        correction_values = form.Qcor.data, form.Hcor.data, form.EFFcor.data
        correction_needed = _correction_needed(correction_values, pump_char)

        if all(correction_values):
            if correction_needed:
                flash(u'Corrected PumpCharacteristic data:', category='success')
                pump_char.correct(*correction_values)
                form.populate_from_obj(pump_char)

        elif any(correction_values):
            flash('You need to specify all 3 correction values to make effect.', category='danger')

        # Save only if no correction values were specified,
        # i.e. data was manually tested previously. after last correction.
        if form.validate() and form.save_submit.data and not correction_needed:
            if not char_id:
                pump_char.pump_id = pump_id
                db.session.add(pump_char)
            db.session.commit()
            flash('Pump characterictic saved succesfully.', category='success')
            return redirect(url_for('pumps.pump', pump_id=pump_id))

    return render_template(
        'pumps/edit_charactericstic.html',
        form=form,
        pump_char=pump_char,
    )


def _correction_needed(correction_values, pump_char):
    # correction_values = form.Qcor.data, form.Hcor.data, form.EFFcor.data
    return all(correction_values) and max(
            (correction_values[0] - pump_char.Qbep) / pump_char.Qbep,
            (correction_values[1] - pump_char.Hbep) / pump_char.Hbep,
            (correction_values[2] - pump_char.EFFcor) / pump_char.EFFcor,
    ) > 0.01


@blueprint.route('/delete_pump_characteristic/<int:char_id>/')
def delete_pump_characteristic(char_id):
    char = PumpCharacteristic.query.get_or_404(char_id)
    if char.deleted_at:
        char.deleted_at = None
    else:
        char.deleted_at = datetime.datetime.utcnow()

    db.session.commit()
    flash('Saved.', category='success')
    return redirect(request.referrer)
