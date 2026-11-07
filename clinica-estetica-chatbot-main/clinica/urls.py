from django.urls import path
from . import views

urlpatterns = [
    path('mensagem/', views.processar_mensagem, name='mensagem'),
]