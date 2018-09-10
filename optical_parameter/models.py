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
    #def pagename(self):
        #return '%s %s %s' % (self.book, self.shelf, self.page)
    def __str__(self):
        return 'Material: %s; Type: %s; Source: %s; Range: %s-%s \u03BCm' % (self.book, self.shelf, self.page, self.rangeMin, self.rangeMax)
    class Meta:
        verbose_name_plural = "Pages"
        #order_with_respect_to = 'pageid'
    # created_at = models.DateTimeField(default = datetime.now, blank = True)
    # insert_user = models.CharField(max_length=30, default='admin')

class Refractiveindex(models.Model):
    pageid = models.ForeignKey('Pages', on_delete=models.CASCADE)
    wave = models.FloatField()
    refindex = models.FloatField()
    #class Meta:
        #order_with_respect_to = 'pageid'

class Extcoeff(models.Model):
    pageid = models.ForeignKey('Pages', on_delete=models.CASCADE)
    wave = models.FloatField()
    coeff = models.FloatField()
    #class Meta:
        #order_with_respect_to = 'pageid'

# class Film(models.Model):
#     SHELF_OPTION = (
#         ('main','common inorganic materials'),
#         ('organic','organic materials'),
#         ('glass','glass'),
#         ('other','miscellaneous and composite materials'),
#     )
#     type = models. CharField(max_length = 10, choices = SHELF_OPTION)
#     material = models.CharField(max_length = 30)
#     # resource = models.CharField(max_length=50, null=True)
#     thickness = models.FloatField()
#     layer_sequence = models.IntegerField()
#     def __str__(self):
#         return 'Material: %s; Type: %s; Thickness: %s nm; Layer: %s' % (self.book, self.shelf, self.thickness, self.layer_sequence)
#
# class NewFilm(ModelForm):
#     class Meta:
#         model = Film
#         fields = ['type', 'material', 'thickness', 'layer_sequence']
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['material'].queryset = Pages.objects.none()
#         # self.fields['resource'].queryset = Pages.objects.none()

class Film(models.Model):
    type = models. CharField(max_length = 50, null=True)
    material = models.CharField(max_length = 50, null=True)
    # resource = models.CharField(max_length=50, null=True)
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
    # type = models. CharField(max_length = 10)
    # material = models.CharField(max_length = 30)
    # # resource = models.CharField(max_length=50, null=True)
    # thickness = models.FloatField()
    # layer_sequence = models.IntegerField()

# class TestNewFilm(forms.Form):
#     type = models. CharField(max_length = 10)
#     material = models.CharField(max_length = 30)
#     # resource = models.CharField(max_length=50, null=True)
#     thickness = models.FloatField()
#     layer_sequence = models.IntegerField()





