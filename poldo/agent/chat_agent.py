import google.generativeai as genai
import json
from .models import HomelabModel, ConversationModel
import os
import logging
logger = logging.getLogger(__name__)

class ChatAgent:
    """
    CONTROLLER - Camada de Controle (MVC)
    
    Esta classe atua como parte da camada Controller do padrão MVC,
    coordenando a comunicação entre Model (dados) e View (interface).
    Usa Gemini AI para processar perguntas sobre homelabs.
    """
    
    def __init__(self):
        # Configuração da API do Gemini
        self.api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=self.api_key)
        
        # CONTROLLER: Usa os Models para acessar dados
        self.homelab_model = HomelabModel()  # Model para dados dos homelabs
        self.conversation_model = ConversationModel()  # Model para conversas
        
        # Configura o modelo Gemini
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Carrega os dados dos homelabs para contexto
        self.homelabs_data = self.homelab_model.get_all_homelabs()
        
        # Cria o contexto inicial para o Gemini
        self._setup_context()
    
    def _setup_context(self):
        """Configura o contexto inicial com dados dos homelabs"""
        homelabs_json = json.dumps(self.homelabs_data, indent=2, ensure_ascii=False)
        
        self.system_prompt = f"""
Você é o Poldo, um assistente especializado em monitoramento de homelabs. 

DADOS DOS HOMELABS DISPONÍVEIS:
{homelabs_json}

INSTRUÇÕES:
1. Responda APENAS com base nos dados fornecidos acima
2. Se o usuário perguntar sobre um homelab que não existe, informe os homelabs disponíveis
3. Seja direto e objetivo nas respostas
4. Use emojis quando apropriado para tornar as respostas mais amigáveis
5. Se perguntarem sobre status completo, liste todas as métricas do homelab
6. Se perguntarem sobre uma métrica específica, foque apenas nela
7. Sempre responda em português brasileiro

EXEMPLOS DE RESPOSTAS:
- Para "qual a cpu do homelab-dev?": "🔍 homelab-dev - CPU: 45%"
- Para "status do homelab-test": Liste todas as métricas do homelab-test
- Para homelab inexistente: "❌ Homelab não encontrado. Homelabs disponíveis: homelab-dev, homelab-test, homelab-prod"
"""

    def process_question(self, question):
        """
        Processa a pergunta do usuário usando Gemini AI e retorna uma resposta apropriada
        
        Args:
            question (str): Pergunta do usuário
            
        Returns:
            str: Resposta formatada pelo Gemini
        """
        try:
            # Cria o prompt completo com contexto e pergunta
            full_prompt = f"{self.system_prompt}\n\nPERGUNTA DO USUÁRIO: {question}"
            
            # Gera resposta usando Gemini
            logger.info(full_prompt)
            response = self.model.generate_content(full_prompt)
            logger.info(response.text.strip())
            # Retorna a resposta do Gemini
            return response.text.strip()
            
        except Exception as e:
            # Em caso de erro na API, retorna uma resposta de fallback
            return f"❌ Erro ao processar pergunta: {str(e)}\n\nPor favor, tente novamente ou verifique sua conexão."
    
    def process_question_with_history(self, question, conversation_id=None):
        """
        CONTROLLER: Processa a pergunta do usuário usando Models e Gemini AI
        
        Args:
            question (str): Pergunta do usuário
            conversation_id (str): ID da conversa (opcional)
            
        Returns:
            tuple: (resposta, conversation_id)
        """
        # CONTROLLER: Usa o Model para gerenciar conversas
        if not conversation_id:
            conversation_id = self.conversation_model.get_current_conversation_id()
        
        # CONTROLLER: Usa o Model para adicionar pergunta ao histórico
        self.conversation_model.add_message(conversation_id, 'user', question)
        
        # CONTROLLER: Usa o Model para obter contexto do histórico
        history_context = self.conversation_model.get_conversation_context(conversation_id)
        
        try:
            # CONTROLLER: Cria o prompt completo com contexto e histórico
            full_prompt = f"{self.system_prompt}\n\n{history_context}\n\nPERGUNTA DO USUÁRIO: {question}"
            
            # CONTROLLER: Gera resposta usando Gemini
            response = self.model.generate_content(full_prompt)
            answer = response.text.strip()
            
            # CONTROLLER: Usa o Model para adicionar resposta ao histórico
            self.conversation_model.add_message(conversation_id, 'bot', answer)
            
            return answer, conversation_id
            
        except Exception as e:
            error_msg = f"❌ Erro ao processar pergunta: {str(e)}\n\nPor favor, tente novamente ou verifique sua conexão."
            
            # CONTROLLER: Usa o Model para adicionar erro ao histórico
            self.conversation_model.add_message(conversation_id, 'bot', error_msg)
            
            return error_msg, conversation_id
    
    # CONTROLLER: Métodos de delegação para o Model
    def start_new_conversation(self):
        """CONTROLLER: Delega para o Model"""
        return self.conversation_model.start_new_conversation()
    
    def get_current_conversation_id(self):
        """CONTROLLER: Delega para o Model"""
        return self.conversation_model.get_current_conversation_id()
    
    def reset_conversation(self):
        """CONTROLLER: Delega para o Model"""
        return self.conversation_model.reset_conversation()
    
    def get_conversation_history(self, conversation_id=None):
        """CONTROLLER: Delega para o Model"""
        return self.conversation_model.get_conversation_history(conversation_id)
    
    def get_all_conversations(self):
        """CONTROLLER: Delega para o Model"""
        return self.conversation_model.get_all_conversations()
    
    def switch_conversation(self, conversation_id):
        """CONTROLLER: Delega para o Model"""
        return self.conversation_model.switch_conversation(conversation_id)
