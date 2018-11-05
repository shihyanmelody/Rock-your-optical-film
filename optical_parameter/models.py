from django.db import models
from django.forms import ModelForm
from django import forms
import matplotlib
from datetime import datetime

# Create your models here.

class Pages(models.Model):
    SHELF_OPTION = (
        ('main','some common inorganic materials'),
        ('organic','organic materials'),
        ('glass','glass'),
        ('other','miscellaneous and composite materials'),
        ('3d','data for fun')
    )
    pageid = models.IntegerField(primary_key=True)
    shelf = models. CharField(max_length = 10, choices = SHELF_OPTION)
    book = models.CharField(max_length = 30)
    page = models.CharField(max_length=50)
    filepath = models.CharField(max_length=200, null=True, blank=True)
    hasrefractive = models.BooleanField()
    hasextinction = models.BooleanField()
    rangeMin = models.FloatField()
    rangeMax = models.FloatField()
    points = models.IntegerField()
    def __str__(self):
        return 'Material: %s; Type: %s; Source: %s; Range: %s-%s \u03BCm' % (self.book, self.shelf, self.page, self.rangeMin, self.rangeMax)
    class Meta:
        verbose_name_plural = "Pages"


class Refractiveindex(models.Model):
    pageid = models.ForeignKey('Pages', on_delete=models.CASCADE)
    wave = models.FloatField()
    refindex = models.FloatField()


class Extcoeff(models.Model):
    pageid = models.ForeignKey('Pages', on_delete=models.CASCADE)
    wave = models.FloatField()
    coeff = models.FloatField()


class Film(models.Model):
    type = models. CharField(max_length = 50, null=True)
    material = models.CharField(max_length = 50, null=True)
    thickness = models.FloatField(null=True)
    layer_sequence = models.IntegerField(primary_key=True)
    class Meta:
        order_with_respect_to = 'layer_sequence'
    def __str__(self):
        return 'Material: %s; : %s; Thickness: %s nm; Layer: %s' % (self.material, self.type, self.thickness, self.layer_sequence)

class NewFilm(ModelForm):
    class Meta:
        model= Film
        fields = ['type', 'material', 'thickness', 'layer_sequence']

class OptimalFilmDesign(models.Model):
    filmtypes = (('Antireflection','Minimize the reflection'),
        ('Highreflection','Maximize the reflection'))
    type_1 = models. CharField(max_length = 50, null=False)
    material_1 = models.CharField(max_length = 50, null=False)
    type_2 = models. CharField(max_length = 50, null=True)
    material_2 = models.CharField(max_length = 50, null=True)
    type_3 = models. CharField(max_length = 50, null=True)
    material_3 = models.CharField(max_length = 50, null=True)
    type_4 = models. CharField(max_length = 50, null=True)
    material_4 = models.CharField(max_length = 50, null=True)
    type_substrate = models. CharField(max_length = 50, null=True)
    material_substrate = models.CharField(max_length = 50, null=True)
    wave_min = models.FloatField(null=False)
    wave_max = models.FloatField(null=False)
    max_thickness = models.FloatField(null=False)
    filmtype = models.CharField(max_length = 50, choices = filmtypes)
    class Meta:
        order_with_respect_to = 'type_substrate'
    def __str__(self):
        return 'Filmtype: %s; Substrate: %s; Materials: %s, %s, %s, %s; Wavelength: %s - %s;'  % (self.filmtype, self.material_substrate, self.material_1, self.material_2, self.material_3, self.material_4, self.wave_min, self.wave_max)

class FormOptimalFilmDesign(ModelForm):
    class Meta:
        model = OptimalFilmDesign
        fields = ['type_1', 'material_1', 'type_2', 'material_2', 'type_3', 'material_3', 'type_4', 'material_4', 'type_substrate', 'material_substrate', 'wave_min', 'wave_max', 'max_thickness', 'filmtype']





