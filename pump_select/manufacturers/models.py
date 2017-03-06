# -*- coding: utf-8 -*-
from pump_select.database import Column, Model, SurrogatePK, db, Timestamps


class PumpManufacturer(Timestamps, SurrogatePK, Model):
    name = Column(db.String(80), unique=True, nullable=False)


class MotorManufacturer(Timestamps, SurrogatePK, Model):
    name = Column(db.String(80), unique=True, nullable=False)
