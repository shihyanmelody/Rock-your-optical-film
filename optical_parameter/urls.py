from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('materials/',views.materials, name = 'materials'),
    path('details/<id>/', views.details, name='details'),
    path('design/', views.design, name='design'),
    path('film/', views.testfilm, name='testfilm'),
    path('film/update/<id>/', views.updatelayer, name='updatelayer'),
    path('design/film/delete/<id>/', views.dellayer, name='dellayer'),
    path('visualization/', views.visualize, name='visualize'),
    path('optimal/optimalfilm/', views.optimalfilm, name='optimalfilm'),
    path('optimal/list/', views.optimallist, name='optimallist'),
    path('optimal/list/optimal/delete/<id>/', views.deloptimaldesign, name='deloptimaldesign'),
    path('optimal/list/optimal/result/<id>/', views.calculateoptimaldesign, name='calculateoptimaldesign'),

    path('test/', views.my_view, name='my_view'),
    path('signup/', views.SignUp.as_view(), name='signup'),

];