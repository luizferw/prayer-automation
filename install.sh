#!/bin/bash

# Script de instalação para o Sistema de Automação para Captura de Pedidos de Oração do YouTube
# Este script instala todas as dependências necessárias e configura o ambiente

echo "Iniciando instalação do Sistema de Automação para Captura de Pedidos de Oração..."
echo "--------------------------------------------------------------------"

# Verificar se o Python 3.8+ está instalado
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Python 3 não encontrado. Por favor, instale o Python 3.8 ou superior."
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ $PYTHON_MAJOR -lt 3 ] || ([ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -lt 8 ]); then
    echo "❌ Versão do Python incompatível: $PYTHON_VERSION. É necessário Python 3.8 ou superior."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION encontrado."

# Instalar dependências
echo "Instalando dependências..."
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib gspread

if [ $? -ne 0 ]; then
    echo "❌ Falha ao instalar dependências. Verifique sua conexão com a internet e tente novamente."
    exit 1
fi

echo "✅ Dependências instaladas com sucesso."

# Verificar arquivos de credenciais
echo "Verificando arquivos de credenciais..."

if [ ! -f "client_secret.json" ]; then
    echo "⚠️ Arquivo client_secret.json não encontrado."
    echo "  Você precisará obter este arquivo do Google Cloud Console."
    echo "  Consulte a documentação (README.md) para instruções detalhadas."
fi

if [ ! -f "service_account.json" ]; then
    echo "⚠️ Arquivo service_account.json não encontrado."
    echo "  Você precisará obter este arquivo do Google Cloud Console."
    echo "  Consulte a documentação (README.md) para instruções detalhadas."
fi

# Verificar permissões de execução
echo "Configurando permissões de execução..."
chmod +x prayer_automation.py
chmod +x youtube_chat_monitor.py
chmod +x google_sheets_integration.py
chmod +x test_prayer_automation.py

echo "✅ Permissões configuradas."

echo "--------------------------------------------------------------------"
echo "✅ Instalação concluída!"
echo ""
echo "Para executar o sistema, use o comando:"
echo "  python3 prayer_automation.py"
echo ""
echo "Para mais informações, consulte o arquivo README.md"
echo "--------------------------------------------------------------------"

