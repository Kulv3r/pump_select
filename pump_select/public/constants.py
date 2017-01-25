# -*- coding: utf-8 -*-
from pump_select.utils import Constant


class RPM(Constant):
    RPM_3000 = 2950
    RPM_1500 = 1480
    RPM_1000 = 980
    RPM_750 = 740


RPM.repr = dict([(rpm, str(rpm)) for rpm in RPM.ALL_])

CORRECTION_ACCURACY = 10**(-5)
