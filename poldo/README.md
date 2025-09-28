# Poldo - Projeto Django MVC

Este é um projeto Django simples que demonstra o padrão MVC (Model-View-Controller) através de um sistema de chat para consultar informações de homelabs.

## 📁 Estrutura do Projeto

```
poldo/
├── poldo/                    # Configurações do projeto Django
│   ├── __init__.py
│   ├── settings.py           # Configurações do Django
│   ├── urls.py              # URLs principais
│   └── wsgi.py
├── agent/                    # App principal
│   ├── __init__.py
│   ├── models.py            # MODEL - HomelabModel
│   ├── views.py             # CONTROLLER - chat_view
│   ├── chat_agent.py        # CONTROLLER - ChatAgent
│   ├── urls.py              # URLs do app
│   ├── data/                # Dados dos homelabs
│   │   └── homelabs.json    # Arquivo JSON com dados
│   └── templates/           # VIEW - Templates HTML
│       └── agent/
│           └── chat.html    # Template principal
├── manage.py
└── README.md
```

## 🏗️ Arquitetura MVC

### Model (Camada de Dados)
- **HomelabModel** (`agent/models.py`): Gerencia os dados dos homelabs carregados do arquivo JSON
- Responsabilidades:
  - Carregar dados do arquivo `homelabs.json`
  - Fornecer métodos para buscar homelabs específicos
  - Retornar métricas individuais ou status completo

### Controller (Camada de Controle)
- **chat_view** (`agent/views.py`): View do Django que processa requisições HTTP
- **ChatAgent** (`agent/chat_agent.py`): Lógica de negócio para interpretar perguntas
- Responsabilidades:
  - Receber requisições do usuário
  - Processar perguntas usando expressões regulares
  - Coordenar comunicação entre Model e View
  - Determinar qual resposta retornar

### View (Camada de Apresentação)
- **chat.html** (`agent/templates/agent/chat.html`): Interface HTML
- Responsabilidades:
  - Apresentar formulário para perguntas
  - Exibir respostas formatadas
  - Interface visual para o usuário

## 🚀 Como Executar o Projeto

### 1. Ativar o Ambiente Virtual
```bash
source /home/ubuntu/Projeto/poldo-devops-agent/env/bin/activate
```

### 2. Navegar para o Diretório do Projeto
```bash
cd /home/ubuntu/Projeto/poldo-devops-agent/poldo
```

### 3. Instalar Dependências (se necessário)
```bash
pip install django
```

### 4. Executar Migrações (opcional - para banco SQLite)
```bash
python manage.py migrate
```

### 5. Iniciar o Servidor de Desenvolvimento
```bash
python manage.py runserver
```

### 6. Acessar a Aplicação
Abra seu navegador e acesse: `http://127.0.0.1:8000/chat/`

## 💡 Exemplos de Uso

### Perguntas Suportadas:
- "qual a cpu do homelab-dev?"
- "como está a memória do homelab-test?"
- "status do homelab-prod"
- "quantos containers docker tem o homelab-dev?"
- "qual o IP do homelab-test?"
- "qual a porta do homelab-prod?"

### Respostas Esperadas:
- **Métrica específica**: "🔍 homelab-dev - Cpu: 45%"
- **Status completo**: Lista todas as métricas do homelab
- **Homelab não encontrado**: Lista homelabs disponíveis

## 📊 Dados dos Homelabs

O arquivo `agent/data/homelabs.json` contém dados de exemplo:

```json
{
  "homelab-dev": {
    "nome": "Homelab Principal",
    "cpu": "45%",
    "memoria": "65%",
    "ram": "8GB",
    "docker": "12 containers ativos",
    "portas": ["80", "443", "22", "8080"],
    "rede": "192.168.1.100",
    "status": "online"
  },
  // ... outros homelabs
}
```

## 🔧 Funcionalidades

- ✅ Interface web simples e responsiva
- ✅ Interpretação de perguntas em português
- ✅ Busca por homelabs específicos
- ✅ Consulta de métricas individuais
- ✅ Status completo de homelabs
- ✅ Validação de dados
- ✅ Tratamento de erros
- ✅ Design moderno e intuitivo

## 🎯 Objetivos de Aprendizado

Este projeto demonstra:
- Separação clara de responsabilidades (MVC)
- Processamento de linguagem natural simples
- Integração entre diferentes camadas
- Manipulação de dados JSON
- Interface web básica com Django
