# -*- coding: utf-8 -*-
from numpy.polynomial import polynomial as P

from pump_select import data
from pump_select.loggers import logger
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

    def vals(self, steps=100):
        min_x, max_x = self.limits

        step = round((max_x - min_x) / steps, 1)

        x_vals = [round(min_x + step * i, 0) for i in range(steps + 1)]

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
        attrs = (
            # values populated by the form
            'H', 'Q_H',
            'EFF', 'Q_EFF',
            'NPSHr', 'Q_NPSHr',
            'Qcor', 'Hcor', 'EFFcor',
            'H_Q_polynom_n',
            'EFF_Q_polynom_n',
            'NPSHr_Q_polynom_n ',
            'rpm_preset', 'rpm_custom',

            'EFF_max', 'Qbep', 'Hbep'
        )
        for attr in attrs:
            val = kwargs.get(attr, None)
            setattr(self, attr, val)

    @property
    def limits(self):
        # Get calculating limits of Q
        series = self.Q_H, self.Q_EFF, self.Q_NPSHr
        limit_from = min([i[0] for i in series])
        limit_to = max(i[-1] for i in series)
        return limit_from, limit_to

    def polynom(self, func_name):
        """
        :param func_name: <string> like 'H(Q)', 'EFF(Q)'
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

        self.EFF_max, self.Qbep = bep
        self.Hbep = P.polyval(self.Qbep, H_Q_polynom.polynom)
        return True

    @property
    def rpm(self):
        return self.rpm_preset or self.rpm_custom

    @property
    def ns(self):
        return 3.65 * rpm * ((self.Qbep / 3600.0)**0.5) / (self.Hbep**0.75)
