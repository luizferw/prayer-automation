#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para validar o sistema de automação para captura de pedidos de oração.
Este script testa os componentes individuais e o sistema completo.
"""

from ..src.prayer_automation import PrayerRequestAutomation
from ..src.google_sheets_integration import GoogleSheetsIntegration
from ..src.youtube_chat_monitor import detectar_pedido_oracao, extrair_nome, extrair_conteudo, normalizar_texto
import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import json

# Importar módulos personalizados
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class TestDeteccaoPedidosOracao(unittest.TestCase):
    """
    Testes para o algoritmo de detecção de pedidos de oração.
    """

    def test_normalizar_texto(self):
        """Testa a função de normalização de texto."""
        texto = "Olá, por favor orem pela minha mãe!"
        resultado = normalizar_texto(texto)
        self.assertEqual(resultado, "ola, por favor orem pela minha mae!")

    def test_detectar_pedido_oracao_positivo(self):
        """Testa a detecção de pedidos de oração com casos positivos."""
        casos_teste = [
            "Por favor, orem pela minha mãe que está no hospital",
            "Peço oração pela saúde do meu pai",
            "Ore por mim, estou com problemas financeiros",
            "Preciso de oração para conseguir um emprego",
            "Intercedam por minha família"
        ]

        for caso in casos_teste:
            e_pedido, nome, conteudo, pontuacao = detectar_pedido_oracao(
                caso, "Autor Teste")
            self.assertTrue(e_pedido, f"Falha ao detectar pedido: '{caso}'")
            self.assertIsNotNone(
                nome, f"Nome não extraído corretamente para: '{caso}'")
            self.assertIsNotNone(
                conteudo, f"Conteúdo não extraído corretamente para: '{caso}'")

    def test_extrair_nome(self):
        """Testa a extração do nome da pessoa que precisa de oração."""
        casos_teste = [
            ("Ore por Maria que está doente", "maria"),
            ("Peço oração pelo João", "joao"),
        ]

        for caso, esperado in casos_teste:
            nome = extrair_nome(normalizar_texto(caso))
            self.assertEqual(
                nome, esperado, f"Falha ao extrair nome de: '{caso}'")

    def test_extrair_conteudo(self):
        """Testa a extração do conteúdo do pedido de oração."""
        texto = "Peço oração pela minha mãe que está no hospital"
        conteudo = extrair_conteudo(normalizar_texto(texto))
        self.assertIn("hospital", conteudo)


class TestGoogleSheetsIntegration(unittest.TestCase):
    """
    Testes para a integração com Google Sheets.
    """

    @patch('gspread.authorize')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_autenticacao(self, mock_creds, mock_authorize):
        """Testa a autenticação com o Google Sheets."""
        # Configurar mocks
        mock_client = MagicMock()
        mock_authorize.return_value = mock_client

        # Criar arquivo de credenciais temporário para teste
        with open('test_creds.json', 'w') as f:
            json.dump({}, f)

        try:
            # Testar autenticação
            sheets = GoogleSheetsIntegration('test_creds.json')
            self.assertEqual(sheets.client, mock_client)

            # Verificar se os métodos foram chamados corretamente
            mock_creds.assert_called_once()
            mock_authorize.assert_called_once()
        finally:
            # Limpar arquivo temporário
            if os.path.exists('test_creds.json'):
                os.remove('test_creds.json')

    @patch('gspread.authorize')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_criar_planilha(self, mock_creds, mock_authorize):
        """Testa a criação de uma planilha."""
        # Configurar mocks
        mock_client = MagicMock()
        mock_planilha = MagicMock()
        mock_folha = MagicMock()

        mock_client.create.return_value = mock_planilha
        mock_planilha.sheet1 = mock_folha
        mock_authorize.return_value = mock_client

        # Criar arquivo de credenciais temporário para teste
        with open('test_creds.json', 'w') as f:
            json.dump({}, f)

        try:
            # Testar criação de planilha
            sheets = GoogleSheetsIntegration('test_creds.json')
            resultado = sheets.criar_planilha("Teste")

            # Verificar se os métodos foram chamados corretamente
            mock_client.create.assert_called_once_with("Teste")
            mock_folha.update_title.assert_called_once()
            mock_folha.update.assert_called_once()
            mock_folha.format.assert_called_once()

            self.assertEqual(resultado, mock_planilha)
        finally:
            # Limpar arquivo temporário
            if os.path.exists('test_creds.json'):
                os.remove('test_creds.json')

    @patch('gspread.authorize')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_adicionar_pedido_oracao(self, mock_creds, mock_authorize):
        """Testa a adição de um pedido de oração à planilha."""
        # Configurar mocks
        mock_client = MagicMock()
        mock_planilha = MagicMock()
        mock_folha = MagicMock()

        mock_planilha.sheet1 = mock_folha
        mock_authorize.return_value = mock_client

        # Criar arquivo de credenciais temporário para teste
        with open('test_creds.json', 'w') as f:
            json.dump({}, f)

        try:
            # Testar adição de pedido de oração
            sheets = GoogleSheetsIntegration('test_creds.json')
            resultado = sheets.adicionar_pedido_oracao(
                mock_planilha, "2025-04-25 18:00:00", "Autor", "Maria", "Saúde")

            # Verificar se os métodos foram chamados corretamente
            mock_folha.append_row.assert_called_once_with(
                ["2025-04-25 18:00:00", "Autor", "Maria", "Saúde"])

            self.assertTrue(resultado)
        finally:
            # Limpar arquivo temporário
            if os.path.exists('test_creds.json'):
                os.remove('test_creds.json')


class TestPrayerRequestAutomation(unittest.TestCase):
    """
    Testes para o sistema completo de automação.
    """

    @patch('prayer_automation.obter_credenciais')
    @patch('prayer_automation.build')
    @patch('prayer_automation.GoogleSheetsIntegration')
    def test_inicializacao(self, mock_sheets, mock_build, mock_creds):
        """Testa a inicialização do sistema de automação."""
        # Configurar mocks
        mock_youtube = MagicMock()
        mock_sheets_instance = MagicMock()

        mock_build.return_value = mock_youtube
        mock_sheets.return_value = mock_sheets_instance

        # Testar inicialização
        automacao = PrayerRequestAutomation(
            'yt_creds.json', 'sheets_creds.json')
        resultado = automacao.inicializar()

        # Verificar se os métodos foram chamados corretamente
        mock_creds.assert_called_once_with('yt_creds.json')
        mock_build.assert_called_once()
        mock_sheets.assert_called_once_with('sheets_creds.json')

        self.assertTrue(resultado)
        self.assertEqual(automacao.youtube, mock_youtube)
        self.assertEqual(automacao.sheets, mock_sheets_instance)

    @patch('prayer_automation.obter_credenciais')
    @patch('prayer_automation.build')
    @patch('prayer_automation.GoogleSheetsIntegration')
    @patch('prayer_automation.obter_live_chat_id')
    def test_configurar_chat(self, mock_chat_id, mock_sheets, mock_build, mock_creds):
        """Testa a configuração do chat ao vivo."""
        # Configurar mocks
        mock_youtube = MagicMock()
        mock_sheets_instance = MagicMock()

        mock_build.return_value = mock_youtube
        mock_sheets.return_value = mock_sheets_instance
        mock_chat_id.return_value = "test_chat_id"

        # Testar configuração do chat
        automacao = PrayerRequestAutomation(
            'yt_creds.json', 'sheets_creds.json')
        automacao.youtube = mock_youtube
        resultado = automacao.configurar_chat("video_id")

        # Verificar se os métodos foram chamados corretamente
        mock_chat_id.assert_called_once_with(mock_youtube, "video_id")

        self.assertTrue(resultado)
        self.assertEqual(automacao.live_chat_id, "test_chat_id")

    @patch('prayer_automation.obter_credenciais')
    @patch('prayer_automation.build')
    @patch('prayer_automation.GoogleSheetsIntegration')
    def test_processar_pedidos_oracao(self, mock_sheets, mock_build, mock_creds):
        """Testa o processamento de pedidos de oração."""
        # Configurar mocks
        mock_youtube = MagicMock()
        mock_sheets_instance = MagicMock()
        mock_planilha = MagicMock()

        mock_build.return_value = mock_youtube
        mock_sheets.return_value = mock_sheets_instance
        mock_sheets_instance.adicionar_pedido_oracao.return_value = True

        # Criar mensagens de teste
        mensagens = [
            {
                'snippet': {
                    'type': 'textMessageEvent',
                    'displayMessage': 'Ore por minha mãe que está doente',
                    'publishedAt': '2025-04-25T18:00:00Z'
                },
                'authorDetails': {
                    'displayName': 'Autor Teste'
                }
            },
            {
                'snippet': {
                    'type': 'textMessageEvent',
                    'displayMessage': 'Olá, como vai o culto?',
                    'publishedAt': '2025-04-25T18:01:00Z'
                },
                'authorDetails': {
                    'displayName': 'Outro Autor'
                }
            }
        ]

        # Testar processamento de pedidos
        automacao = PrayerRequestAutomation(
            'yt_creds.json', 'sheets_creds.json')
        automacao.sheets = mock_sheets_instance
        automacao.planilha = mock_planilha

        with patch('prayer_automation.processar_mensagens') as mock_processar:
            # Configurar mock para retornar um pedido de oração
            mock_processar.return_value = [
                ('2025-04-25 18:00:00', 'Autor Teste', 'minha mãe', 'está doente')
            ]

            resultado = automacao.processar_pedidos_oracao(mensagens)

            # Verificar se os métodos foram chamados corretamente
            mock_processar.assert_called_once_with(mensagens)
            mock_sheets_instance.adicionar_pedido_oracao.assert_called_once()

            self.assertEqual(resultado, 1)


def executar_testes():
    """
    Executa todos os testes unitários.
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Adicionar testes à suite
    suite.addTests(loader.loadTestsFromTestCase(TestDeteccaoPedidosOracao))
    suite.addTests(loader.loadTestsFromTestCase(TestGoogleSheetsIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPrayerRequestAutomation))

    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)

    return resultado.wasSuccessful()


if __name__ == "__main__":
    print("Executando testes do sistema de automação para captura de pedidos de oração...")
    sucesso = executar_testes()

    if sucesso:
        print("\n✅ Todos os testes foram executados com sucesso!")
        sys.exit(0)
    else:
        print("\n❌ Alguns testes falharam. Verifique os detalhes acima.")
        sys.exit(1)
