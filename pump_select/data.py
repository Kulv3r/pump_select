# -*- coding: utf-8 -*-


def list_zip(*lists):
    return [list(i) for i in zip(*lists)]


# Q(H)
Q_H = [0.0, 54.53, 115.0, 174.7, 240.6, 289.7, 345.2, 393.6, 439.7, 478.2, 518.7, 564.6, 626.0, 676.6,
       730.7, 770.9, 817.8, 863.2, 911.5, 955.2]
H = [116.5, 116.3, 116.3, 116.2, 115.9, 115.5, 114.7, 113.7, 112.7, 111.6, 110.3, 108.5, 105.9,
     103.4, 100.6, 98.41, 95.67, 92.88, 89.74, 86.7]
H_Q = list_zip(Q_H, H)

# Q(кпд)
Q_eff = [0.0, 16.62, 37.61, 55.15, 78.37, 103.3, 130, 160.8, 198.9, 233.7, 275.4, 330.2, 379.3, 436.9,
         492.1, 546.7, 612.1, 659.5, 709.6, 777.2, 831.7, 890.7, 956.1]
eff = [0, 6, 13, 19, 26, 33, 39, 46, 53, 59, 65, 71, 75, 78, 80, 81, 82, 82, 82, 81, 80, 79, 78]
eff_Q = list_zip(eff, Q_eff)

# Q(NPSHr)
Q_NPSHr = [184, 351, 500, 619, 700, 850]
NPSHr = [1.4, 1.7, 2.2, 2.8, 4.1, 6.2]
NPSHr_Q = list_zip(NPSHr, Q_NPSHr)
