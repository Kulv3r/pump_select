# -*- coding: utf-8 -*-
from numpy.polynomial import polynomial as P

from pump_select import data
from pump_select.data import list_zip
from pump_select.public.constants import *


class Polynom(object):
    def __init__(self, x_series, y_series, n_poly_power, limits):
        self.x_series = x_series
        self.y_series = y_series
        self.n_poly_power = n_poly_power
        self.limits = self._correct_limits(limits)

        self.polynom = self._get_polynom()

    def _get_polynom(self):
        return P.polyfit(self.x_series, self.y_series, self.n_poly_power)

    def _correct_limits(self, limits):
        min_x, max_x = limits
        if max_x < min_x:
            min_x, max_x = max_x, min_x
        return min_x, max_x

    def points(self):
        # Convert points to chart series
        return data.list_zip(self.x_series, self.y_series)

    def vals(self, x_vals=None):
        if not x_vals:
            min_x, max_x = self.limits
            x_vals = range(int(min_x), int(max_x)+1)

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


class Pump(object):
    def __init__(self, **kwargs):
        # values populated by the form LATER, not during the INIT
        self.H = kwargs.get('H')
        self.Q_H = kwargs.get('Q_H')
        self.EFF = kwargs.get('EFF')
        self.Q_EFF = kwargs.get('Q_EFF')
        self.NPSHr = kwargs.get('NPSHr')
        self.Q_NPSHr = kwargs.get('Q_NPSHr')
        self.Qcor = kwargs.get('Qcor')
        self.Hcor = kwargs.get('Hcor')
        self.EFFcor = kwargs.get('EFFcor')
        self.H_Q_polynom_n = kwargs.get('H_Q_polynom_n')
        self.EFF_Q_polynom_n = kwargs.get('EFF_Q_polynom_n')
        self.NPSHr_Q_polynom_n = kwargs.get('NPSHr_Q_polynom_n')
        self.rpm_preset = kwargs.get('rpm_preset')
        self.rpm_custom = kwargs.get('rpm_custom')

        self.EFFmax = None
        self.Qbep = None
        self.Hbepself = None

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
        series = self.Q_H, self.Q_EFF, self.Q_NPSHr
        limit_from = min([i[0] for i in series])
        limit_to = max(i[-1] for i in series)
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
        EFF_Q_polynom = self.polynom('EFF(Q)')
        H_Q_polynom = self.polynom('H(Q)')

        bep = EFF_Q_polynom.max_val(self.limits)
        if not bep:
            return

        self.EFFmax, self.Qbep = bep
        self.Hbep = P.polyval(self.Qbep, H_Q_polynom.polynom)

        return True

    @property
    def rpm(self):
        return self.rpm_preset or self.rpm_custom

    @property
    def ns(self):
        if self.Qbep and self.Hbep:
            return 3.65 * self.rpm * ((self.Qbep / 3600.0)**0.5) / (self.Hbep**0.75)

    @property
    def PWR(self):
        # P2(Q) = ro * g * H(Q) * (Q / 3600) / кпд(Q) / 1000[кВт].
        EFF_Q_polynom = self.polynom('EFF(Q)')
        EFFs = [eff for (q, eff) in EFF_Q_polynom.vals(x_vals=self.Q_H)]

        H_Q_EFF = zip(self.H, self.Q_H, EFFs)
        powers = [WATER.ro * PHYSICS.g * H * Q/3600 / EFF / 1000
                  for (H, Q, EFF) in H_Q_EFF]
        return powers

    @property
    def Q_PWR(self):
        return self.Q_H

    @property
    def PWR_Q_polynom_n(self):
        return self.EFF_Q_polynom_n

    @property
    def chart_data(self):
        return [
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
                'points': self.polynom('EFF(Q)').points(),
            },
            {
                'name': 'Power(Q)',
                'data': self.polynom('PWR(Q)').vals(),
                'suffix': 'kW',
                'valueDecimals': 2,
                'points': [],
            },
            {
                'name': 'NPSHr(Q)',
                'data': self.polynom('NPSHr(Q)').vals(),
                'suffix': 'm',
                'valueDecimals': 2,
                'points': self.polynom('NPSHr(Q)').points(),
            },
        ]