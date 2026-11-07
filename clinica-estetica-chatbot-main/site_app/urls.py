from django.urls import path
from . import views

app_name = 'site_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('servicos/', views.servicos, name='servicos'),
    path('contato/', views.contato, name='contato'),
    path('politica-de-privacidade/', views.privacidade, name='privacidade'),
    path('quem-somos/', views.sobre, name='sobre'),
]
