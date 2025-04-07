elementos = {
    'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8, 'F': 9,
    'Ne': 10, 'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15, 'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19,
    'Ca': 20, 'Sc': 21, 'Ti': 22, 'V': 23, 'Cr': 24, 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29,
    'Zn': 30, 'Ga': 31, 'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35, 'Kr': 36, 'Rb': 37, 'Sr': 38, 'Y': 39,
    'Zr': 40, 'Nb': 41, 'Mo': 42, 'Tc': 43, 'Ru': 44, 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49,
    'Sn': 50, 'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54, 'Cs': 55, 'Ba': 56, 'La': 57, 'Ce': 58, 'Pr': 59,
    'Nd': 60, 'Pm': 61, 'Sm': 62, 'Eu': 63, 'Gd': 64, 'Tb': 65, 'Dy': 66, 'Ho': 67, 'Er': 68, 'Tm': 69,
    'Yb': 70, 'Lu': 71, 'Hf': 72, 'Ta': 73, 'W': 74, 'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78, 'Au': 79,
    'Hg': 80, 'Tl': 81, 'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85, 'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89,
    'Th': 90, 'Pa': 91, 'U': 92, 'Np': 93, 'Pu': 94, 'Am': 95, 'Cm': 96, 'Bk': 97, 'Cf': 98, 'Es': 99,
    'Fm': 100, 'Md': 101, 'No': 102, 'Lr': 103, 'Rf': 104, 'Db': 105, 'Sg': 106, 'Bh': 107, 'Hs': 108, 'Mt': 109,
    'Ds': 110, 'Rg': 111, 'Cn': 112, 'Nh': 113, 'Fl': 114, 'Mc': 115, 'Lv': 116, 'Ts': 117, 'Og': 118
}

densidad = {
    1: 0.08988,  # Hidrógeno
    2: 0.1786,   # Helio
    3: 0.534,    # Litio
    4: 1.85,     # Berilio
    5: 2.34,     # Boro
    6: 2.267,    # Carbono
    7: 1.251,    # Nitrógeno
    8: 1.429,    # Oxígeno
    9: 1.696,    # Flúor
    10: 0.9002,  # Neón
    11: 0.971,   # Sodio
    12: 1.738,   # Magnesio
    13: 2.698,   # Aluminio
    14: 2.329,   # Silicio
    15: 1.82,    # Fósforo
    16: 2.07,    # Azufre
    17: 3.214,   # Cloro
    18: 1.784,   # Argón
    19: 0.862,   # Potasio
    20: 1.55,    # Calcio
    21: 2.989,   # Escandio
    22: 4.54,    # Titanio
    23: 6.11,    # Vanadio
    24: 7.15,    # Cromo
    25: 7.44,    # Manganeso
    26: 7.874,   # Hierro
    27: 8.9,     # Cobalto
    28: 8.908,   # Níquel
    29: 8.96,    # Cobre
    30: 7.134,   # Zinc
    31: 5.91,    # Galio
    32: 5.323,   # Germanio
    33: 5.776,   # Arsénico
    34: 4.809,   # Selenio
    35: 3.12,    # Bromo
    36: 3.75,    # Kriptón
    37: 1.532,   # Rubidio
    38: 2.64,    # Estroncio
    39: 4.469,   # Itrio
    40: 6.506,   # Circonio
    41: 8.57,    # Niobio
    42: 10.22,   # Molibdeno
    43: 11.5,    # Tecnecio
    44: 12.37,   # Rutenio
    45: 12.41,   # Rodio
    46: 12.02,   # Paladio
    47: 10.49,   # Plata
    48: 8.65,    # Cadmio
    49: 7.31,    # Indio
    50: 7.287,   # Estaño
    51: 6.685,   # Antimonio
    52: 6.24,    # Telurio
    53: 4.93,    # Yodo
    54: 5.894,   # Xenón
    55: 1.873,   # Cesio
    56: 3.594,   # Bario
    57: 6.162,   # Lantano
    58: 6.77,    # Cerio
    59: 6.773,   # Praseodimio
    60: 7.007,   # Neodimio
    61: 7.26,    # Prometio
    62: 7.52,    # Samario
    63: 5.243,   # Europio
    64: 7.895,   # Gadolinio
    65: 8.229,   # Terbio
    66: 8.55,    # Disprosio
    67: 8.795,   # Holmio
    68: 9.066,   # Erbio
    69: 9.321,   # Tulio
    70: 6.965,   # Iterbio
    71: 9.84,    # Lutecio
    72: 13.31,   # Hafnio
    73: 16.654,  # Tántalo
    74: 19.25,   # Wolframio
    75: 21.02,   # Renio
    76: 22.59,   # Osmio
    77: 22.56,   # Iridio
    78: 21.45,   # Platino
    79: 19.32,   # Oro
    80: 13.533,  # Mercurio
    81: 11.85,   # Talio
    82: 11.34,   # Plomo
    83: 9.747,   # Bismuto
    84: 9.32,    # Polonio
    85: 6.35,    # Astato
    86: 9.73,    # Radón
    87: 1.87,    # Francio
    88: 5.5      # Radio
}
