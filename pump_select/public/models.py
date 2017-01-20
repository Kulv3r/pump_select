# -*- coding: utf-8 -*-
"""User models."""
import numpy as np
from flask_login import UserMixin

from pump_select.database import Column, Model, SurrogatePK, db, reference_col, relationship, Timestamps
from pump_select.extensions import bcrypt


# class Chart(Timestamps, SurrogatePK, Model):
class Chart(object):
    def __init__(self, xx, yy):
        # x_label = 'x'
        # y_label = 'y'
        self.xx = [1, 2, 3]
        y_vals = [11, 41, 91]

    def polyfit(self, x_vals, y_vals, n):
        # It returns for an n=4
        # [1.16035322e+02, -6.77159076e-04, 7.49052572e-06, -7.71847069e-08, 3.72781671e-11]
        #       A                 B                 C              D               E
        # so formula = A + Bx + Cx**2 + Dx**3 + Ex**4
        return np.polynomial.polynomial.polyfit(x_vals, y_vals, n).tolist()

    def polyval(self, x_vals, coeffs):
        return np.polynomial.polynomial.polyval(x_vals, coeffs).tolist()


    def qweqwe(self):
            x = data.Q1[0]
            max_x = data.Q1[-1]
            if max_x < x:
                x, max_x = max_x, x
            steps = 50
            step = (max_x - x) / steps
            series = []
            while x < (max_x+step):
                # f = p[0] + p[1] * x**1 + p[2] * x**2 + ...
                f = sum([(c * x**p) for p, c in enumerate(polynom)])
                series.append([round(x, 1), round(f, 1)])
                x += step

            polynoms_vals[n] = series