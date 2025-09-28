"""
CONTROLLER - Camada de Controle (MVC)

Este módulo contém a lógica de negócio e controle do sistema.
É responsável por coordenar a comunicação entre Model e View,
processando as requisições e aplicando as regras de negócio.
"""

import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .chat_agent import ChatAgent
from .models import Conversation, Message

# Instância global do ChatAgent (em produção usar cache ou banco de dados)
chat_agent = ChatAgent()


class ChatController:
    """
    CONTROLLER - Classe principal para controle do chat
    
    Gerencia toda a lógica de negócio relacionada ao chat,
    incluindo criação de conversas, envio de mensagens e
    processamento de respostas.
    """
    
    @staticmethod
    def get_or_create_conversation(conversation_id=None):
        """
        Obtém uma conversa existente ou cria uma nova
        
        Args:
            conversation_id (int, optional): ID da conversa
            
        Returns:
            Conversation: Objeto da conversa
        """
        if conversation_id:
            try:
                return get_object_or_404(Conversation, id=conversation_id)
            except:
                return None
        
        return None
    
    @staticmethod
    def create_new_conversation():
        """
        Cria uma nova conversa
        
        Returns:
            Conversation: Nova conversa criada
        """
        return Conversation.objects.create(title="Nova Conversa")
    
    @staticmethod
    def get_conversation_context(conversation_id=None):
        """
        Obtém o contexto completo de uma conversa
        
        Args:
            conversation_id (int, optional): ID da conversa
            
        Returns:
            dict: Contexto com conversa atual, todas as conversas e mensagens
        """
        current_conversation = ChatController.get_or_create_conversation(conversation_id)
        
        if not current_conversation:
            current_conversation = ChatController.create_new_conversation()
        
        all_conversations = Conversation.objects.all()
        chat_messages = current_conversation.messages.all()
        
        return {
            'current_conversation': current_conversation,
            'all_conversations': all_conversations,
            'chat_messages': chat_messages,
            'show_result': False
        }
    
    @staticmethod
    def process_message(question, conversation_id=None):
        """
        Processa uma mensagem do usuário e retorna a resposta
        
        Args:
            question (str): Pergunta do usuário
            conversation_id (int, optional): ID da conversa
            
        Returns:
            dict: Resultado do processamento com HTML das mensagens
        """
        # Obtém ou cria a conversa
        conversation = ChatController.get_or_create_conversation(conversation_id)
        
        if not conversation:
            conversation = ChatController.create_new_conversation()
        
        # Cria mensagem do usuário
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            text=question
        )
        
        # Atualiza o título da conversa se for a primeira mensagem do usuário
        ChatController._update_conversation_title(conversation, question)
        
        # Processa a pergunta usando o ChatAgent
        answer = chat_agent.process_question(question)
        
        # Cria mensagem do bot
        bot_message = Message.objects.create(
            conversation=conversation,
            role='bot',
            text=answer
        )
        
        # Gera HTML das mensagens
        user_html = f'<div class="message-bubble user">{user_message.text}</div>'
        bot_html = f'<div class="message-bubble bot">{bot_message.text}</div>'
        
        return {
            'ok': True,
            'conversation_id': conversation.id,
            'user_html': user_html,
            'bot_html': bot_html
        }
    
    @staticmethod
    def _update_conversation_title(conversation, question):
        """
        Atualiza o título da conversa baseado na primeira pergunta
        
        Args:
            conversation (Conversation): Objeto da conversa
            question (str): Pergunta do usuário
        """
        if conversation.messages.filter(role='user').count() == 1:
            title = question[:40] + "..." if len(question) > 40 else question
            conversation.title = title
            conversation.save()
    
    @staticmethod
    def validate_message_data(data):
        """
        Valida os dados da mensagem recebida
        
        Args:
            data (dict): Dados recebidos
            
        Returns:
            tuple: (is_valid, question, conversation_id, error_message)
        """
        try:
            question = data.get('question', '').strip()
            conversation_id = data.get('conversation_id')
            
            if not question:
                return False, None, None, 'Pergunta não pode estar vazia'
            
            return True, question, conversation_id, None
            
        except Exception as e:
            return False, None, None, f'Erro na validação: {str(e)}'
    
    @staticmethod
    def handle_send_message_request(request):
        """
        Manipula a requisição de envio de mensagem via AJAX
        
        Args:
            request: Objeto request do Django
            
        Returns:
            JsonResponse: Resposta JSON com resultado
        """
        try:
            # Parse do JSON
            data = json.loads(request.body)
            
            # Valida os dados
            is_valid, question, conversation_id, error = ChatController.validate_message_data(data)
            
            if not is_valid:
                return JsonResponse({
                    'ok': False,
                    'error': error
                }, status=400)
            
            # Processa a mensagem
            result = ChatController.process_message(question, conversation_id)
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'ok': False,
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'ok': False,
                'error': f'Erro interno: {str(e)}'
            }, status=500)
