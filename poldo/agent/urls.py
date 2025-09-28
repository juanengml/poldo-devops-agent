from django.urls import path
from . import views

app_name = 'agent'

urlpatterns = [
    # Rota para a página inicial (redireciona para chat)
    path('', views.home_view, name='home'),
    # Rota para a página de chat
    path('chat/', views.chat_view, name='chat'),
    # Rota para nova conversa
    path('new-conversation/', views.new_conversation_view, name='new_conversation'),
    # Rota para envio de mensagens via AJAX
    path('chat/send/', views.send_message, name='send_message'),
]
