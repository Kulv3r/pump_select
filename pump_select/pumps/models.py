# -*- coding: utf-8 -*-
from pprint import pprint

from numpy.polynomial import polynomial as P
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils import ChoiceType

from pump_select.database import Timestamps, SurrogatePK, Model, reference_col, Column
from pump_select.database import relationship
from pump_select.example_data import list_zip
from pump_select.extensions import db
from pump_select.general.constants import *
from pump_select.pumps.constants import SealType, Material


class Pump(Timestamps, SurrogatePK, Model):
    manufacturer_id = reference_col('pump_manufacturer')
    manufacturer = relationship('PumpManufacturer')

    name = Column(db.String(80), unique=True, nullable=False)
    size_type = Column(db.String(80))
    inbound_diameter = Column(db.Float(precision=2))
    inbound_pressure = Column(db.Float(precision=2))
    outbound_diameter = Column(db.Float(precision=2))
    outbound_pressure = Column(db.Float(precision=2))
    seal_type = Column(ChoiceType(choices=SealType.OPTIONS, impl=db.Integer()))
    mass = Column(db.Integer())
    material_body = Column(ChoiceType(choices=Material.OPTIONS, impl=db.Integer()))
    material_wheel = Column(ChoiceType(choices=Material.OPTIONS, impl=db.Integer()))
    material_shaft = Column(ChoiceType(choices=Material.OPTIONS, impl=db.Integer()))
    max_pressure = Column(db.Float(precision=2))
    frequency_regulation_needed = Column(db.Boolean())
    fluid_temp_min = Column(db.Integer())
    fluid_temp_max = Column(db.Integer())

    @property
    def characteristics(self):
        return (
            PumpCharacteristic.query
            .filter(PumpCharacteristic.pump == self)
            .order_by(PumpCharacteristic.Qbep.asc())
        )


class PumpCharacteristic(Timestamps, SurrogatePK, Model):
    pump_id = reference_col('pump')
    pump = relationship('Pump')

    Q_H_polynom = Column(postgresql.ARRAY(db.Integer(), dimensions=1))
    Q_EFF_polynom = Column(postgresql.ARRAY(db.Integer(), dimensions=1))
    Q_PWR_polynom = Column(postgresql.ARRAY(db.Integer(), dimensions=1))
    Q_NPSHr_polynom = Column(postgresql.ARRAY(db.Integer(), dimensions=1))
    rpm = Column(db.Integer())
    EFFmax = Column(db.Float(precision=2))
    Qbep = Column(db.Float(precision=2))
    Hbep = Column(db.Float(precision=2))
    PWRbep = Column(db.Float(precision=2))   # kW, used by pump
    PWR2bep = Column(db.Float(precision=2))  # kW, used by motor
    NPSHrbep = Column(db.Float(precision=2))
    _Qmin = Column(db.Float(precision=2))
    _Qmax = Column(db.Float(precision=2))
    Hmin = Column(db.Float(precision=2))
    Hmax = Column(db.Float(precision=2))
    stages = Column(db.Integer())
    enters = Column(db.Integer())  # pump wheel with 1 or 2 entrances

    def __init__(self, **kwargs):
        # values populated by the form LATER, not during the INIT
        self.H = kwargs.get('H')
        self.Q_H = kwargs.get('Q_H')
        self.EFF = kwargs.get('EFF')
        self.Q_EFF = kwargs.get('Q_EFF')
        self.PWR = kwargs.get('PWR')
        self.Q_PWR = kwargs.get('Q_PWR')
        self.is_EFF_set = None
        self.NPSHr = kwargs.get('NPSHr')
        self.Q_NPSHr = kwargs.get('Q_NPSHr')
        self.Qcor = kwargs.get('Qcor')
        self.Hcor = kwargs.get('Hcor')
        self.EFFcor = kwargs.get('EFFcor')
        self.PWRcor = kwargs.get('PWRcor')
        self.H_Q_polynom_n = kwargs.get('H_Q_polynom_n')
        self.EFF_Q_polynom_n = kwargs.get('EFF_Q_polynom_n')
        self.PWR_Q_polynom_n = kwargs.get('PWR_Q_polynom_n')
        self.NPSHr_Q_polynom_n = kwargs.get('NPSHr_Q_polynom_n')
        self.rpm_preset = kwargs.get('rpm_preset')
        self.rpm_custom = kwargs.get('rpm_custom')

        self.EFFmax = None
        self.PWRbep = None
        self.Hbep = None
        self.Qbep = None
        self.NPSHrbep = None
        self._Qmin = kwargs.get('Qmin')
        self._Qmax = kwargs.get('Qmax')

    def calculate_missing(self):
        if self.EFF and not self.PWR:
            self.is_EFF_set = True
            self.PWR = self.get_PWR()
            self.Q_PWR = self.Q_H
        elif self.PWR and not self.EFF:
            self.is_EFF_set = False
            self.EFF = self.get_EFF()
            self.Q_EFF = self.Q_H
        else:
            raise Exception('Either PWR or EFF should be defined.')

        # Add zero efficiency point
        if self.EFF[0] != 0:
            self.EFF.insert(0, 0)
            self.Q_EFF.insert(0, 0)

    def get_PWR(self):
        # P2(Q) = ro * g * H(Q) * (Q / 3600) / (кпд(Q) * 100%) / 1000 [кВт].
        EFF_Q_polynom = self.polynom('EFF(Q)')
        EFFs = [eff for (q, eff) in EFF_Q_polynom.vals(x_vals=self.Q_H)]

        H_Q_EFF = zip(self.H, self.Q_H, EFFs)
        powers = [WATER.ro * PHYSICS.g * H * (Q / 3600) / (EFF / 100) / 1000
                  for (H, Q, EFF) in H_Q_EFF]
        return powers

    def get_EFF(self):
        # EFF(Q) = ro * g * H(Q) * (Q / 3600) / P(Q) / 1000 * 100%
        PWR_Q_polynom = self.polynom('PWR(Q)')
        PWRs = [pwr for (q, pwr) in PWR_Q_polynom.vals(x_vals=self.Q_H)]

        H_Q_PWR = zip(self.H, self.Q_H, PWRs)
        effs = [WATER.ro * PHYSICS.g * H * (Q / 3600) / PWR / 1000 * 100
                for (H, Q, PWR) in H_Q_PWR]
        return effs

    def correct(self, Qcor, Hcor, EFFcor):
        correcting_coef = Hcor / self.Hbep
        self.H = [val*correcting_coef for val in self.H]

        correcting_coef = EFFcor / self.EFFmax
        self.EFF = [val*correcting_coef for val in self.EFF]

        correcting_coef = Qcor / self.Qbep
        self.Q_H = [val*correcting_coef for val in self.Q_H]
        self.Q_EFF = [val*correcting_coef for val in self.Q_EFF]

        self.get_bep()

    @property
    def limits(self):
        # Get calculating limits of Q
        series = self.Q_H, self.Q_EFF, self.Q_PWR, self.Q_NPSHr
        limit_from = min([i[0] for i in series if i])
        limit_to = max(i[-1] for i in series if i)
        return limit_from, limit_to

    def polynom(self, func_name):
        """
        :param func_name: <string> like 'EFF(Q)'
        Requires self to have these attrs:
            self.EFF
            self.Q_EFF
            self.EFF_Q_polynom_n
        :return: a <Polynom> object
        """
        y_name, x_name = func_name[:-1].split('(')
        n_name = '{y}_{x}_polynom_n'.format(y=y_name, x=x_name)
        x_name = '{x}_{y}'.format(x=x_name, y=y_name)
        x = getattr(self, x_name)
        y = getattr(self, y_name)
        n = getattr(self, n_name)
        return Polynom(x, y, n, self.limits)

    def get_bep(self):
        # Get max efficiency ("bep" - best efficiency point)
        bep = self.polynom('EFF(Q)').max_val(self.limits)
        if not bep:
            return  # i.e. bad data and bep cant be found

        self.EFFmax, self.Qbep = bep
        self.Hbep = P.polyval(self.Qbep, self.polynom('H(Q)').polynom)
        self.PWRbep = P.polyval(self.Qbep, self.polynom('PWR(Q)').polynom)
        self.NPSHrbep = P.polyval(self.Qbep, self.polynom('NPSHr(Q)').polynom)

        return True  # i.e. bep found succesfully

    @property
    def ns(self):
        if self.Qbep and self.Hbep:
            return 3.65 * self.rpm * ((self.Qbep / 3600.0)**0.5) / (self.Hbep**0.75)

    @property
    def chart_data(self):
        all_charts = [
            {
                'name': 'H(Q)',
                'data': self.polynom('H(Q)').vals(),
                'suffix': 'm',
                'valueDecimals': 0,
                'points': self.polynom('H(Q)').points(),
            },
            {
                'name': 'Efficiency(Q)',
                'data': self.polynom('EFF(Q)').vals(),
                'suffix': '%',
                'valueDecimals': 1,
                'points': self.polynom('EFF(Q)').points() if self.is_EFF_set else [],
            },
            {
                'name': 'Power(Q)',
                'data': self.polynom('PWR(Q)').vals(),
                'suffix': 'kW',
                'valueDecimals': 1,
                'points': self.polynom('PWR(Q)').points() if not self.is_EFF_set else [],
            },
            {
                'name': 'NPSHr(Q)',
                'data': self.polynom('NPSHr(Q)').vals(),
                'suffix': 'm',
                'valueDecimals': 2,
                'points': self.polynom('NPSHr(Q)').points(),
            },
        ]
        return all_charts

    @property
    def Qmin(self):
        """ Qmin (application range) = 0.7 Qbep """
        return self._Qmin or int(self.Qbep * 0.7)

    @Qmin.setter
    def Qmin(self, value):
        self._Qmin = value

    @property
    def Qmax(self):
        """ Qmax (application range) = 1.25 Qbep """
        return self._Qmax or int(self.Qbep * 1.25)

    @Qmax.setter
    def Qmax(self, value):
        self._Qmax = value


class Polynom(object):
    def __init__(self, x_series, y_series, n_poly_power, limits):
        self.x_series = x_series
        self.y_series = y_series
        self.n_poly_power = n_poly_power
        self.limits = self._correct_limits(limits)

        self.polynom = self._get_polynom()

    def _get_polynom(self):
        """
        :return: coefficients of:
            p(x) = c_0 + c_1 * x + ... + c_n * x^n
        """
        return P.polyfit(self.x_series, self.y_series, self.n_poly_power)

    def _correct_limits(self, limits):
        min_x, max_x = limits
        if max_x < min_x:
            min_x, max_x = max_x, min_x
        return min_x, max_x

    def points(self):
        # Convert points to chart series
        return list_zip(self.x_series, self.y_series)

    def vals(self, x_vals=None):
        if not x_vals:
            min_x, max_x = self.limits
            x_vals = list(range(int(min_x), int(max_x)+1))

        y_vals = P.polyval(x_vals, self.polynom).tolist()
        y_vals_rounded = [round(i, 2) for i in y_vals]

        return [list(i) for i in zip(x_vals, y_vals_rounded)]

    def max_val(self, limits):
        # Get max efficiency
        poly_der = P.polyder(self.polynom)  # Differentiate a polynomial.
        roots = P.polyroots(poly_der)  # Compute the roots of a polynomial.
        real_roots = [r.real for r in roots if not r.imag]

        # Remove roots out of the limits
        roots_in_limits = [r for r in real_roots if limits[0] < r < limits[1]]

        # Get actual function values for each root (extremum)
        roots_max = [
            (P.polyval(r, self.polynom), r)
            for r in roots_in_limits
        ]
        if not roots_max:
            return

        f_val, root = max(roots_max)
        return f_val, root
