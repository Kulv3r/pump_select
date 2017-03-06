# -*- coding: utf-8 -*-
from pump_select.database import Column, Model, SurrogatePK, db, Timestamps, reference_col
from pump_select.database import relationship


class Motor(Timestamps, SurrogatePK, Model):
    manufacturer_id = reference_col('motor_manufacturer')
    manufacturer = relationship('MotorManufacturer')

    name = Column(db.String(80), unique=True, nullable=False)
    power = Column(db.Float(precision=2))
    voltage = Column(db.Integer())
    current_frequency = Column(db.Integer())
    rpm = Column(db.Integer())
    _ip_protection = Column(db.String(2))
    explosion_protected = Column(db.Boolean())
    mass = Column(db.Integer())

    @property
    def ip_protection(self):
        return 'IP{}'.format(self._protection) if self._protection else None
