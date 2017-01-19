# -*- coding: utf-8 -*-
from pump_select.utils import Constant


class UserSecondFactors(Constant):
    NONE = 0
    SMS = 1
    EMAIL = 2
    
    repr = {
        NONE: u'-',
        SMS: u'SMS',
        EMAIL: u'email',
    }
