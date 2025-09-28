from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from .controller import ChatController

def chat_view(request):
    """
    VIEW - Página principal do chat
    
    Renderiza a interface do chat com o contexto necessário.
    Delega a lógica de negócio para o ChatController.
    """
    conversation_id = request.GET.get('conversation_id')
    
    # Delega para o controller
    context = ChatController.get_conversation_context(conversation_id)
    
    # Se uma nova conversa foi criada, redireciona
    if not conversation_id and context['current_conversation']:
        return redirect(f'/chat/?conversation_id={context["current_conversation"].id}')
    
    return render(request, 'agent/chat.html', context)

def new_conversation_view(request):
    """
    VIEW - Cria uma nova conversa
    
    Delega a criação para o ChatController e redireciona.
    """
    new_conversation = ChatController.create_new_conversation()
    return redirect(f'/chat/?conversation_id={new_conversation.id}')


def home_view(request):
    """
    VIEW - Página inicial
    
    Redireciona automaticamente para a página de chat.
    """
    return redirect('agent:chat')


@require_http_methods(["POST"])
def send_message(request):
    """
    VIEW - Endpoint para envio de mensagens via AJAX
    
    Delega o processamento para o ChatController.
    """
    return ChatController.handle_send_message_request(request)