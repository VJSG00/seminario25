import numpy as np


def bethe_bloch(E, I, rho, Z, A, z=1, m_0=938.272e6):

    # Cálculo de beta y gamma
    beta = np.sqrt(E * (E + 2 * m_0) / ((E + m_0)**2))
    gamma = np.sqrt(1 / (1 - beta**2))

    # Cálculo de W_max
    m_e = 0.51099895e6  # masa del electrón en eV/c^2
    W_max = 2 * m_e * beta**2 * gamma**2  # eV


    argumento = 2 * m_e * beta**2 * gamma**2 * W_max / I**2
    # Ecuación de Bethe y Bloch
    dE_dx = 0.1535e6 * rho * (Z / A) * (z**2 / beta**2) * (np.log(argumento) - 2 * beta**2) #eV/cm
    #print(np.log(argumento))
    return dE_dx  # MeV/cm