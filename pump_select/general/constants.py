# -*- coding: utf-8 -*-
from pump_select.utils import Constant


class PHYSICS(object):
    g = 9.81  # m/s2


class WATER(object):
    ro = 998.2  # kg / m3


class RPM(Constant):
    RPM_3000 = 2950
    RPM_1500 = 1480
    RPM_1000 = 980
    RPM_750 = 745
    RPM_600 = 590


class CurrentFrequencies(Constant):
    FREQ_50 = 50
    FREQ_60 = 60
