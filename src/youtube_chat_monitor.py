#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para monitoramento do chat ao vivo do YouTube e detecção de pedidos de oração.
Este script utiliza a API do YouTube para acessar mensagens do chat ao vivo,
identifica pedidos de oração e os prepara para serem adicionados a uma planilha.
"""

import os
import time
import re
import unicodedata
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

base_dir = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.abspath(base_dir)

# Configurações
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
CLIENT_SECRETS_FILE = os.path.join(
    project_root, 'secrets', 'client_secret.json'
)


def get_user_data_path(filename):
    pasta_dados = os.path.join(os.path.expanduser("~"), ".prayer_automation")
    os.makedirs(pasta_dados, exist_ok=True)
    return os.path.join(pasta_dados, filename)


TOKEN_FILE = get_user_data_path("token.json")


def normalizar_texto(texto):
    """
    Normaliza o texto removendo acentos e convertendo para minúsculas.

    Args:
      texto (str): Texto a ser normalizado

    Returns:
      str: Texto normalizado
    """
    # Remover acentos
    texto_sem_acentos = ''.join(c for c in unicodedata.normalize('NFD', texto)
                                if unicodedata.category(c) != 'Mn')
    # Converter para minúsculas e normalizar espaços
    return ' '.join(texto_sem_acentos.lower().split())


TERMOS_PRIMARIOS = [
    "ore por", "oração por", "orem por", "orar por", "peço oração",
    "pedido de oração", "por favor orem", "intercedam por", "intercessão por"
]

TERMOS_SECUNDARIOS = [
    "preciso de oração", "necessito de oração", "por favor ore",
    "oração para", "ore pela", "ore pelo", "orem pela", "orem pelo"
]

TERMOS_CONTEXTUAIS = [
    "saúde", "doença", "hospital", "cirurgia", "família", "problema",
    "dificuldade", "cura", "libertação", "restauração", "provisão",
    "financeiro", "emprego", "trabalho", "preciso", "ajuda", "socorro",
]

TERMOS_PRIMARIOS = [normalizar_texto(termo) for termo in TERMOS_PRIMARIOS]
TERMOS_SECUNDARIOS = [normalizar_texto(termo) for termo in TERMOS_SECUNDARIOS]
TERMOS_CONTEXTUAIS = [normalizar_texto(termo) for termo in TERMOS_CONTEXTUAIS]

PADROES = [
    r"ore(?:m)?\s+por\s+(?:meu|minha|o|a|os|as)?\s+([^\s,\.]+)",
    r"peço\s+oracao\s+(?:para|por|pela|pelo)\s+(?:meu|minha|o|a|os|as)?\s+([^\s,\.]+)",
    r"preciso\s+de\s+oracao\s+(?:para|por)\s+([^\s,\.]+)",
    r"(?:por\s+favor\s+)?(?:ore|orem|oracao)\s+(?:para|por|pela|pelo)\s+([^\s,\.]+)"
]


def detectar_pedido_oracao(mensagem: str):
    """
    Detecta se uma mensagem contém um pedido de oração.

    Args:
      mensagem (str): Texto da mensagem enviado no chat.

    Returns:
      tuple: (pontuação, probabilidade) onde:
        - pontuacao (int): Pontuação.
        - probabilidade (str): Nível de probabilidade do texto ser um pedido de oração ("Alta", "Média", "Baixa", "Nenhuma").
    """
    texto = normalizar_texto(mensagem)

    pontuacao = 0

    for termo in TERMOS_PRIMARIOS:
        if termo in texto:
            pontuacao += 3
            break

    for termo in TERMOS_SECUNDARIOS:
        if termo in texto:
            pontuacao += 3
            break

    for termo in TERMOS_CONTEXTUAIS:
        if termo in texto:
            pontuacao += 1

    for padrao in PADROES:
        match = re.search(padrao, texto)
        if match:
            pontuacao += 2
            break

    if pontuacao >= 4:
        probabilidade = "Alta"
    elif 2 <= pontuacao <= 3:
        probabilidade = "Média"
    elif pontuacao == 1:
        probabilidade = "Baixa"
    else:
        probabilidade = "Nenhuma"

    return pontuacao, probabilidade


def obter_credenciais(youtube_credentials_path=CLIENT_SECRETS_FILE):
    """
    Obtém as credenciais de autenticação para a API do YouTube.

    Returns:
        Credentials: Objeto de credenciais para a API
    """
    credenciais = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as token_file:
            token_data = json.load(token_file)
        credenciais = Credentials.from_authorized_user_info(token_data, SCOPES)

    if not credenciais or not credenciais.valid:
        if credenciais and credenciais.expired and credenciais.refresh_token:
            credenciais.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                youtube_credentials_path,
                SCOPES
            )
            credenciais = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(credenciais.to_json())

    return credenciais


def obter_live_chat_id(youtube, video_id=None):
    """
    Obtém o ID do chat ao vivo para um vídeo específico ou para a transmissão ao vivo atual.

    Args:
        youtube: Objeto de serviço da API do YouTube
        video_id (str, opcional): ID do vídeo para obter o chat ao vivo

    Returns:
        str: ID do chat ao vivo ou None se não encontrado
    """
    if video_id:
        request = youtube.videos().list(
            part="liveStreamingDetails",
            id=video_id
        )
        response = request.execute()

        if response['items']:
            return response['items'][0].get('liveStreamingDetails', {}).get('activeLiveChatId')
        return None

    request = youtube.liveBroadcasts().list(
        part="snippet,contentDetails",
        broadcastStatus="active",
        maxResults=5
    )
    response = request.execute()

    if response['items']:
        return response['items'][0]['snippet']['liveChatId']

    return None


def obter_mensagens_chat(youtube, live_chat_id, page_token=None):
    """
    Obtém mensagens do chat ao vivo.

    Args:
        youtube: Objeto de serviço da API do YouTube
        live_chat_id (str): ID do chat ao vivo
        page_token (str, opcional): Token para a próxima página de resultados

    Returns:
        tuple: (mensagens, próximo_token, intervalo_polling) onde:
            - mensagens: Lista de mensagens do chat
            - próximo_token: Token para a próxima página
            - intervalo_polling: Tempo em ms para aguardar antes da próxima solicitação
    """
    request = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part="snippet,authorDetails",
        pageToken=page_token
    )
    response = request.execute()

    for mensagem in response['items']:
        if mensagem['snippet']['type'] == 'textMessageEvent':
            texto = mensagem['snippet']['displayMessage']
            autor = mensagem['authorDetails']['displayName']
            print(
                f"[LOG] Comentário recebido: Autor: {autor}, Mensagem: {texto}")

    return (
        response['items'],
        response['nextPageToken'],
        response['pollingIntervalMillis']
    )


def processar_mensagens(mensagens):
    """
    Processa as mensagens do chat para identificar pedidos de oração.

    Args:
        mensagens (list): Lista de mensagens do chat

    Returns:
        list: Lista de pedidos de oração identificados no formato
              [(timestamp, autor, nome, conteúdo), ...]
    """
    pedidos_oracao = []

    for mensagem in mensagens:
        if mensagem['snippet']['type'] != 'textMessageEvent':
            continue

        texto_original = mensagem['snippet']['displayMessage']
        autor = mensagem['authorDetails']['displayName']
        timestamp = mensagem['snippet']['publishedAt']

        pontuacao, probabilidade = detectar_pedido_oracao(texto_original)

        if pontuacao > 0:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            dt_utc_minus_3 = dt - timedelta(hours=3)
            timestamp_formatado = dt_utc_minus_3.strftime('%Y-%m-%d %H:%M:%S')

            nome_autor_processado = processar_nome_autor(autor)
            texto_processado = processar_texto(texto_original)

            pedidos_oracao.append(
                (
                    timestamp_formatado,
                    nome_autor_processado,
                    texto_processado,
                    texto_original,
                    probabilidade
                )
            )

    return pedidos_oracao


def processar_nome_autor(nome_autor: str):
    """
    Processa o nome do autor para que fique com todas as letras minúsculas,
    exceto as primeiras letras de cada palavra, que serão capitalizadas.

    Args:
      nome_autor (str): Nome do autor a ser processado.

    Returns:
      str: Nome do autor formatado.
    """
    return nome_autor.lower().title()


def processar_texto(texto: str):
    """ 
      Processa o texto para torná-lo mais legível e corrigir possíveis erros gramaticais.
    """
    return texto


def monitorar_chat_ao_vivo(youtube, video_id=None):
    """
    Monitora continuamente o chat ao vivo para identificar pedidos de oração.

    Args:
        youtube: Objeto de serviço da API do YouTube
        video_id (str, opcional): ID do vídeo para monitorar o chat

    Returns:
        generator: Gerador que produz pedidos de oração à medida que são identificados
    """
    live_chat_id = obter_live_chat_id(youtube, video_id)

    if not live_chat_id:
        print("Não foi possível encontrar um chat ao vivo.")
        return

    print(f"Monitorando chat ao vivo com ID: {live_chat_id}")

    next_page_token = None

    while True:
        try:
            mensagens, next_page_token, intervalo_polling = obter_mensagens_chat(
                youtube,
                live_chat_id,
                next_page_token
            )

            pedidos = processar_mensagens(mensagens)

            for pedido in pedidos:
                yield pedido

            time.sleep(intervalo_polling / 1000)

        except Exception as e:
            print(f"Erro ao monitorar chat: {e}")
            time.sleep(5)


def main():
    """
    Função principal para demonstrar o monitoramento do chat.
    """
    credenciais = obter_credenciais()
    youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credenciais)

    video_id = input(
        "Digite o ID do vídeo do YouTube: ").strip()

    if not video_id:
        video_id = None

    print("Iniciando monitoramento do chat ao vivo...")
    print("Pressione Ctrl+C para encerrar.")

    try:
        for timestamp, autor, texto_processado, texto_original, probabilidade in monitorar_chat_ao_vivo(youtube, video_id):
            print(f"\n[{timestamp}] Pedido de oração detectado:")
            print(f"Autor da mensagem: {autor}")
            print(f"Conteúdo do pedido: {texto_processado}")
            print(f"Conteúdo original do pedido: {texto_original}")
            print(f"Probabilidade: {probabilidade}")
            print("-" * 50)

    except KeyboardInterrupt:
        print("\nMonitoramento encerrado pelo usuário.")


if __name__ == "__main__":
    main()
