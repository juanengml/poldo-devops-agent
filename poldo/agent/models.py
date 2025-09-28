import json
import os
import uuid
from datetime import datetime
from django.conf import settings
from django.db import models

class ConversationModel:
    """
    MODEL - Camada de Dados para Conversas (MVC)
    
    Esta classe representa a camada Model do padrão MVC para gerenciar
    conversas e histórico de mensagens.
    """
    
    def __init__(self):
        # Em produção, isso seria um banco de dados
        # Por simplicidade, usando memória
        self.conversations = {}
        self.current_conversation_id = None
    
    def start_new_conversation(self):
        """Inicia uma nova conversa"""
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = {
            'id': conversation_id,
            'created_at': datetime.now().isoformat(),
            'messages': [],
            'title': 'Nova Conversa'
        }
        self.current_conversation_id = conversation_id
        return conversation_id
    
    def get_current_conversation_id(self):
        """Retorna o ID da conversa atual"""
        if not self.current_conversation_id:
            return self.start_new_conversation()
        return self.current_conversation_id
    
    def reset_conversation(self):
        """Reseta a conversa atual"""
        if self.current_conversation_id:
            self.conversations[self.current_conversation_id]['messages'] = []
        return self.current_conversation_id
    
    def get_conversation_history(self, conversation_id=None):
        """Retorna o histórico de uma conversa"""
        if not conversation_id:
            conversation_id = self.get_current_conversation_id()
        
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]['messages']
        return []
    
    def get_all_conversations(self):
        """Retorna todas as conversas"""
        return list(self.conversations.values())
    
    def switch_conversation(self, conversation_id):
        """Muda para uma conversa específica"""
        if conversation_id in self.conversations:
            self.current_conversation_id = conversation_id
            return True
        return False
    
    def add_message(self, conversation_id, message_type, content):
        """Adiciona uma mensagem ao histórico"""
        if conversation_id not in self.conversations:
            conversation_id = self.start_new_conversation()
        
        message = {
            'type': message_type,  # 'user' ou 'bot'
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        self.conversations[conversation_id]['messages'].append(message)
        
        # Atualiza título da conversa se for a primeira mensagem do usuário
        if message_type == 'user' and len(self.conversations[conversation_id]['messages']) == 1:
            self.conversations[conversation_id]['title'] = content[:50] + "..." if len(content) > 50 else content
        
        return message
    
    def get_conversation_context(self, conversation_id=None, max_messages=20):
        """Retorna o contexto do histórico para o Gemini"""
        if not conversation_id:
            conversation_id = self.get_current_conversation_id()
        
        messages = self.get_conversation_history(conversation_id)
        
        if len(messages) <= 2:  # Apenas a pergunta atual
            return ""
        
        # Pega as últimas mensagens
        recent_messages = messages[-max_messages:]
        
        history_text = "HISTÓRICO DA CONVERSA:\n"
        for msg in recent_messages[:-2]:  # Exclui a pergunta atual
            if msg['type'] == 'user':
                history_text += f"Usuário: {msg['content']}\n"
            else:
                history_text += f"Poldo: {msg['content']}\n"
        
        history_text += "\n"
        return history_text

class HomelabModel:
    """
    MODEL - Camada de Dados (MVC)
    
    Esta classe representa a camada Model do padrão MVC.
    É responsável por carregar e gerenciar os dados dos homelabs
    a partir do arquivo JSON.
    """
    
    def __init__(self):
        # Caminho para o arquivo JSON dos homelabs
        self.data_file = os.path.join(os.path.dirname(__file__), 'data', 'homelabs.json')
        self._data = None
    
    def _load_data(self):
        """Carrega os dados do arquivo JSON"""
        if self._data is None:
            try:
                with open(self.data_file, 'r', encoding='utf-8') as file:
                    self._data = json.load(file)
            except FileNotFoundError:
                self._data = {}
            except json.JSONDecodeError:
                self._data = {}
        return self._data
    
    def get_all_homelabs(self):
        """
        Retorna todos os homelabs disponíveis
        
        Returns:
            dict: Dicionário com todos os homelabs
        """
        return self._load_data()
    
    def get_homelab_by_name(self, homelab_name):
        """
        Busca um homelab específico pelo nome
        
        Args:
            homelab_name (str): Nome do homelab (ex: homelab-dev)
            
        Returns:
            dict: Dados do homelab ou None se não encontrado
        """
        data = self._load_data()
        return data.get(homelab_name)
    
    def get_homelab_metric(self, homelab_name, metric):
        """
        Busca uma métrica específica de um homelab
        
        Args:
            homelab_name (str): Nome do homelab
            metric (str): Nome da métrica (cpu, memoria, ram, etc.)
            
        Returns:
            str: Valor da métrica ou None se não encontrado
        """
        homelab = self.get_homelab_by_name(homelab_name)
        if homelab:
            return homelab.get(metric)
        return None
    
    def get_available_metrics(self):
        """
        Retorna lista de métricas disponíveis
        
        Returns:
            list: Lista de métricas disponíveis
        """
        data = self._load_data()
        if data:
            # Pega as chaves do primeiro homelab como exemplo
            first_homelab = list(data.values())[0]
            return list(first_homelab.keys())
        return []
    
    def get_homelab_names(self):
        """
        Retorna lista de nomes dos homelabs
        
        Returns:
            list: Lista de nomes dos homelabs
        """
        return list(self._load_data().keys())


# Django Models para persistência em banco de dados
class Conversation(models.Model):
    """
    Model Django para representar uma conversa no chat
    """
    title = models.CharField(max_length=200, default="Nova Conversa")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Conversa"
        verbose_name_plural = "Conversas"
    
    def __str__(self):
        return self.title


class Message(models.Model):
    """
    Model Django para representar uma mensagem em uma conversa
    """
    ROLE_CHOICES = [
        ('user', 'Usuário'),
        ('bot', 'Bot'),
    ]
    
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name="messages"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
    
    def __str__(self):
        return f"{self.role}: {self.text[:50]}..."