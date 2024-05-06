from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('saisie', views.saisie, name='saisie'),
    path('result/<int:nb_variable><int:nb_contraintes>', views.result, name='result'),
]
