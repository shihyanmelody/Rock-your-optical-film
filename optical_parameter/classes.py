from .models import Pages, Refractiveindex, Extcoeff, Film, NewFilm,  OptimalFilmDesign, FormOptimalFilmDesign
from scipy import interpolate
import numpy as np
import tmm as tmm
import math as math




class OpticalMaterial:
    def __init__(self, id):
        self.name = None
        self.id = id
        self.wave = []
        self.n = []
        self.k = []
        self.refractivecomplex = []
        self.minwave = 0
        self.maxwave = 0
        self.kexist = False

    def get_refractives(self):
        self.name = list(Pages.objects.filter(pageid=self.id).values_list("book", flat=True))[0]
        wavelength = list(Refractiveindex.objects.filter(pageid_id=self.id).values_list("wave", flat=True))
        wavenm = [i * 1000 for i in wavelength]
        self.wave = wavenm
        n_re = list(Refractiveindex.objects.filter(pageid_id=self.id).values_list("refindex", flat=True))
        self.n = n_re
        mat_excoeff = Extcoeff.objects.filter(pageid_id=self.id)
        k_ex = [0.000000001] * len(wavelength)
        if mat_excoeff.exists():
            k_ex = list(mat_excoeff.values_list("coeff", flat=True))
            self.kexist = False
        self.k = k_ex
        self.minwave = 1000*min(wavelength)
        self.maxwave = 1000*max(wavelength)
        for wa in range(0, len(wavenm)):
            self.refractivecomplex.append(complex(n_re[wa], k_ex[wa]))

    def get_refractive_function(self):
        return interpolate.interp1d(self.wave, self.n, kind='quadratic')

    def get_complex_function(self):
        # print(len(self.wave), len(self.refractivecomplex))
        return interpolate.interp1d(self.wave, self.refractivecomplex, kind='quadratic')


