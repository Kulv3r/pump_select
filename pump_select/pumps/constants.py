# -*- coding: utf-8 -*-

from pump_select.utils import Constant


class PumpCategory(Constant):
    # End-suction pumps
    ## Horizontal
    OH1 = 1  # 'End-suction pump (OH1)'
    OH2 = 2  # 'End-suction pump, centerline mounted (OH2)'
    OHM = 5  # 'End-suction pump, Monobloc'
    OHL = 6  # 'End-suction pump, In-Line'
    ## Vertical
    OH3 = 3  # 'End-suction pump, In-Line'
    OH4 = 4  # 'End-suction pumps > Vertical > Monoblock (OH4, OH5)'

    # Between-bearings pumps
    ## Axial split
    BB1 = 10  # Double entry, Axially Split Casing pump, One stage
    BBC = 11  # Two Stage, Axially Split Pump
    ## Multi-stage
    BB4 = 12  # Between bearings multi-stage radially split pump
    BBV = 13  # vertical multistage centrifugal in-line pumps

    repr = {
        OH1: 'End-suction pumps > Horizontal > Standard (OH1)',
        OH2: 'End-suction pumps > Horizontal > Centerline mounted (OH2)',
        OHM: 'End-suction pumps > Horizontal > Monoblock',
        OHL: 'End-suction pumps > Horizontal > In-Line',
        OH3: 'End-suction pumps > Vertical > In-Line (OH3)',
        OH4: 'End-suction pumps > Vertical > Monoblock (OH4, OH5)',
        BB1: 'Between-bearings pumps > Axial split > Double entry, one stage (BB1)',
        BBC: 'Between-bearings pumps > Axial split > Double entry, two stages (BB1)',
        BB4: 'Between-bearings pumps > Multi-stage > Radially splitted (BB4)',
        BBV: 'Between-bearings pumps > Multi-stage > Vertical centrifugal in-line',
    }


class SealTypes(Constant):
    GLAND = 1  # gland seal
    MECHANICAL = 2  # Mechanical seal
    DOUBLE = 3  # Double mechanical seal

    repr = {
        GLAND: 'Gland seal',
        MECHANICAL: 'Mechanical seal',
        DOUBLE: 'Double Mechanical seal',
    }
