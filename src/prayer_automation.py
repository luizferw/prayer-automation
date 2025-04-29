#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Automação para Captura de Pedidos de Oração do YouTube

Este script integra o monitoramento do chat ao vivo do YouTube com o Google Sheets
para capturar pedidos de oração e adicioná-los automaticamente a uma planilha online ou local.
"""

from google_sheets_integration import GoogleSheetsIntegration, ExcelLocalIntegration
from youtube_chat_monitor import (
    obter_credenciais,
    obter_live_chat_id,
    obter_mensagens_chat,
    processar_mensagens,
    build
)

import time
from datetime import datetime
from logger_config import logger


class PrayerRequestAutomation:
    """
    Classe principal para automação de captura de pedidos de oração.
    """

    def __init__(self, youtube_credentials_file, sheets_credentials_file, use_local_excel=False):
        """
        Inicializa o sistema de automação.

        Args:
            youtube_credentials_file (str): Caminho para o arquivo de credenciais do YouTube
            sheets_credentials_file (str): Caminho para o arquivo de credenciais do Google Sheets
            use_local_excel (bool): Define se o sistema usará um arquivo Excel local em vez do Google Sheets
        """
        self.youtube_credentials_file = youtube_credentials_file
        self.sheets_credentials_file = sheets_credentials_file
        self.use_local_excel = use_local_excel
        self.youtube = None
        self.sheets = None
        self.planilha = None
        self.live_chat_id = None
        self.next_page_token = None
        self.running = False

    def inicializar(self):
        """
        Inicializa as conexões com as APIs do YouTube e Google Sheets ou Excel local.

        Returns:
            bool: True se a inicialização foi bem-sucedida, False caso contrário
        """
        try:
            logger.info("Inicializando conexão com a API do YouTube...")
            credenciais = obter_credenciais(self.youtube_credentials_file)
            self.youtube = build('youtube', 'v3', credentials=credenciais)

            if self.use_local_excel:
                logger.info("Inicializando integração com o Excel local...")
                self.sheets = ExcelLocalIntegration()
            else:
                logger.info("Inicializando conexão com o Google Sheets...")
                self.sheets = GoogleSheetsIntegration(
                    self.sheets_credentials_file)

            return True

        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")
            return False

    def configurar_planilha(self, identificador=None):
        """
        Configura a planilha ou arquivo Excel para armazenar os pedidos de oração.

        Args:
            identificador (str, opcional): Título, URL ou ID da planilha existente (apenas para Google Sheets)

        Returns:
            bool: True se a configuração foi bem-sucedida, False caso contrário
        """
        try:
            if self.use_local_excel:
                logger.info(
                    "Usando arquivo Excel local para armazenar os pedidos de oração.")
                self.planilha = {
                    "url": "Arquivo Excel Local: " + self.sheets.arquivo_excel
                }
            else:
                if identificador:
                    logger.info(f"Abrindo planilha existente: {identificador}")
                    self.planilha = self.sheets.abrir_planilha(identificador)
                    if not self.planilha:
                        logger.error(
                            f"Não foi possível abrir a planilha: {identificador}"
                        )
                        return False
                # else:
                #     titulo = f"Pedidos de Oração - {datetime.now().strftime('%d/%m/%Y')}"
                #     logger.info(f"Criando nova planilha: {titulo}")
                #     self.planilha = self.sheets.criar_planilha(titulo)

            logger.info("Planilha ou arquivo Excel configurado com sucesso.")
            return True

        except Exception as e:
            logger.error(
                f"Erro na configuração da planilha ou arquivo Excel: {e}")
            return False

    def configurar_chat(self, video_id=None):
        """
        Configura o monitoramento do chat ao vivo.

        Args:
            video_id (str, opcional): ID do vídeo do YouTube para monitorar

        Returns:
            bool: True se a configuração foi bem-sucedida, False caso contrário
        """
        try:
            logger.info(
                f"Obtendo ID do chat ao vivo{' para o vídeo ' + video_id if video_id else ''}...")
            self.live_chat_id = obter_live_chat_id(self.youtube, video_id)

            if not self.live_chat_id:
                logger.error("Não foi possível encontrar um chat ao vivo.")
                return False

            logger.info(
                f"Chat ao vivo configurado com ID: {self.live_chat_id}")
            return True

        except Exception as e:
            logger.error(f"Erro na configuração do chat: {e}")
            return False

    def processar_pedidos_oracao(self, mensagens):
        """
        Processa todas as mensagens do chat e adiciona apenas os pedidos de oração à planilha ou arquivo Excel.

        Args:
            mensagens (list): Lista de mensagens do chat

        Returns:
            int: Número de pedidos de oração processados
        """
        pedidos_oracao = processar_mensagens(mensagens)

        contador = 0

        for timestamp, autor, conteudo, conteudoOriginal, probabilidade in pedidos_oracao:
            logger.info(f"Pedido de oração detectado: {autor} - {conteudo}")

            if self.use_local_excel:
                sucesso = self.sheets.adicionar_pedido_oracao(
                    timestamp, autor, conteudo, conteudoOriginal, probabilidade
                )
            else:
                sucesso = self.sheets.adicionar_pedido_oracao(
                    self.planilha, timestamp, autor, conteudo, conteudoOriginal, probabilidade
                )

            if sucesso:
                logger.info("Pedido de oração adicionado com sucesso.")
                contador += 1
            else:
                logger.error("Erro ao adicionar pedido de oração.")

        return contador

    def iniciar_monitoramento(self, intervalo_atualizacao=None):
        """
        Inicia o monitoramento contínuo do chat ao vivo.

        Args:
            intervalo_atualizacao (int, opcional): Intervalo mínimo em segundos entre atualizações
        """
        if not self.live_chat_id or not self.planilha:
            logger.error("Chat ao vivo ou planilha não configurados.")
            return

        logger.info(
            f"Iniciando monitoramento do chat ao vivo: {self.live_chat_id}")
        logger.info(
            f"Pedidos de oração serão adicionados à planilha: {self.planilha['url'] if isinstance(self.planilha, dict) else self.planilha.url}")

        self.running = True
        total_pedidos = 0

        try:
            while self.running:
                mensagens, self.next_page_token, intervalo_polling = obter_mensagens_chat(
                    self.youtube,
                    self.live_chat_id,
                    self.next_page_token
                )

                novos_pedidos = self.processar_pedidos_oracao(mensagens)
                total_pedidos += novos_pedidos

                if novos_pedidos > 0:
                    logger.info(
                        f"{novos_pedidos} novos pedidos de oração adicionados à planilha."
                    )

                if intervalo_atualizacao:
                    intervalo_espera = max(
                        intervalo_atualizacao, intervalo_polling / 1000
                    )
                else:
                    intervalo_espera = intervalo_polling / 1000

                logger.debug(
                    f"Aguardando {intervalo_espera:.2f} segundos antes da próxima verificação..."
                )
                time.sleep(intervalo_espera)

        except KeyboardInterrupt:
            logger.info("Monitoramento interrompido pelo usuário.")
        except Exception as e:
            logger.error(f"Erro durante o monitoramento: {e}")
        finally:
            self.running = False
            logger.info(
                f"Monitoramento finalizado. Total de pedidos processados: {total_pedidos}")

    def parar_monitoramento(self):
        """
        Para o monitoramento do chat ao vivo.
        """
        self.running = False
        logger.info("Solicitação para parar o monitoramento recebida.")
