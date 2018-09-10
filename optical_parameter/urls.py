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
    #path('player/', views.player, name='player'),

    #path('details/<int:id_input>/', views.details, name='details'),
    #path('newpost/', views.newpost, name = 'newpost'),
];