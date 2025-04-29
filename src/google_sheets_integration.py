#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para integração com Google Sheets.
Este script permite adicionar pedidos de oração a uma planilha do Google Sheets.
"""

import os
import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import openpyxl
import time

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(base_dir)

SERVICE_ACCOUNT_FILE = os.path.join(
    project_root, 'secrets', 'service_account.json'
)


class GoogleSheetsIntegration:
    """
    Classe para gerenciar a integração com o Google Sheets.
    """

    def __init__(self, credentials_file=SERVICE_ACCOUNT_FILE):
        """
        Inicializa a integração com o Google Sheets.

        Args:
            credentials_file (str): Caminho para o arquivo de credenciais da conta de serviço
        """
        self.credentials_file = credentials_file
        self.client = self._autenticar()

    def _autenticar(self):
        """
        Autentica com o Google Sheets usando credenciais de conta de serviço.

        Returns:
            gspread.Client: Cliente autenticado do gspread
        """
        try:
            if not os.path.exists(self.credentials_file):
                raise FileNotFoundError(
                    f"Arquivo de credenciais não encontrado: {self.credentials_file}"
                )

            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=SCOPES
            )

            return gspread.authorize(credentials)

        except Exception as e:
            print(f"Erro na autenticação com o Google Sheets: {e}")
            raise

    def criar_planilha(self, titulo):
        """
        Cria uma nova planilha com o título especificado.

        Args:
            titulo (str): Título da nova planilha

        Returns:
            gspread.Spreadsheet: Objeto da planilha criada
        """
        try:
            planilha = self.client.create(titulo)
            folha = planilha.sheet1
            folha.update_title("Pedidos de Oração")
            cabecalhos = ["Data/Hora", "Autor da Mensagem",
                          "Pedido de Oração", "Texto Original", "Probabilidade"]
            folha.update('A1:E1', [cabecalhos])
            folha.format('A1:E1', {
                'textFormat': {'bold': True},
                'horizontalAlignment': 'CENTER',
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })

            folha.columns_auto_resize(0, 5)

            print(f"Planilha criada com sucesso: {planilha.url}")
            return planilha

        except Exception as e:
            print(f"Erro ao criar planilha: {e}")
            raise

    def abrir_planilha(self, identificador):
        """
        Abre uma planilha existente pelo título, URL ou ID e adiciona cabeçalhos se necessário.

        Args:
            identificador (str): Título, URL ou ID da planilha

        Returns:
            gspread.Spreadsheet: Objeto da planilha aberta
        """
        try:
            if identificador.startswith('http'):
                planilha = self.client.open_by_url(identificador)
            elif len(identificador) > 30:
                planilha = self.client.open_by_key(identificador)
            else:
                planilha = self.client.open(identificador)

            # Verificar e adicionar cabeçalhos se necessário
            folha = planilha.sheet1
            cabecalhos_existentes = folha.row_values(1)
            cabecalhos_necessarios = ["Data/Hora", "Autor da Mensagem",
                                      "Pedido de Oração", "Texto Original", "Probabilidade"]

            if not cabecalhos_existentes or cabecalhos_existentes != cabecalhos_necessarios:
                folha.update('A1:E1', [cabecalhos_necessarios])
                folha.format('A1:E1', {
                    'textFormat': {'bold': True},
                    'horizontalAlignment': 'CENTER',
                    'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                })

            return planilha

        except gspread.exceptions.SpreadsheetNotFound:
            print(f"Planilha não encontrada: {identificador}")
            return None
        except Exception as e:
            print(f"Erro ao abrir planilha: {e}")
            raise

    def adicionar_pedido_oracao(self, planilha, timestamp, autor, conteudo, conteudoOriginal, probabilidade):
        """
        Adiciona um pedido de oração à planilha.

        Args:
            planilha (gspread.Spreadsheet): Objeto da planilha
            timestamp (str): Data e hora do pedido
            autor (str): Nome do autor da mensagem
            conteudo (str): Conteúdo do pedido de oração
            conteudoOriginal (str): Conteúdo original do pedido
            probabilidade (str): Probabilidade associada ao pedido (ex: "Alta", "Média", "Baixa")

        Returns:
            bool: True se o pedido foi adicionado com sucesso, False caso contrário
        """
        try:
            folha = planilha.sheet1
            dados = [
                timestamp,
                autor,
                conteudo,
                conteudoOriginal,
                probabilidade
            ]
            folha.append_row(dados)
            time.sleep(5)
            folha.columns_auto_resize(0, 5)

            return True

        except Exception as e:
            print(f"Erro ao adicionar pedido de oração: {e}")
            return False

    def compartilhar_planilha(self, planilha, email, role='reader'):
        """
        Compartilha a planilha com um usuário específico.

        Args:
            planilha (gspread.Spreadsheet): Objeto da planilha
            email (str): Endereço de e-mail do usuário
            role (str): Papel do usuário ('reader', 'writer', 'owner')

        Returns:
            bool: True se a planilha foi compartilhada com sucesso, False caso contrário
        """
        try:
            planilha.share(email, perm_type='user', role=role)
            print(f"Planilha compartilhada com {email} como {role}")
            return True

        except Exception as e:
            print(f"Erro ao compartilhar planilha: {e}")
            return False

    def obter_todos_pedidos(self, planilha):
        """
        Obtém todos os pedidos de oração da planilha.

        Args:
            planilha (gspread.Spreadsheet): Objeto da planilha

        Returns:
            list: Lista de pedidos de oração
        """
        try:
            folha = planilha.sheet1

            return folha.get_all_records()

        except Exception as e:
            print(f"Erro ao obter pedidos de oração: {e}")
            return []


class ExcelLocalIntegration:
    """
    Classe para gerenciar a exportação e edição de dados do chat em um arquivo Excel local.
    """

    def __init__(self, arquivo_excel="dados_chat.xlsx"):
        """
        Inicializa a integração com o arquivo Excel local.

        Args:
            arquivo_excel (str): Nome do arquivo Excel local.
        """
        self.arquivo_excel = arquivo_excel
        self._inicializar_arquivo()

    def _inicializar_arquivo(self):
        """
        Cria o arquivo Excel se ele não existir e adiciona cabeçalhos.
        """
        if not os.path.exists(self.arquivo_excel):
            workbook = openpyxl.Workbook()
            folha = workbook.active
            folha.title = "Pedidos de Oração"
            cabecalhos = ["Data/Hora", "Autor da Mensagem", "Pedido de Oração"]
            folha.append(cabecalhos)
            workbook.save(self.arquivo_excel)

    def adicionar_pedido_oracao(self, timestamp, autor, conteudo):
        """
        Adiciona um pedido de oração ao arquivo Excel local.

        Args:
            timestamp (str): Data e hora do pedido.
            autor (str): Nome do autor da mensagem.
            conteudo (str): Conteúdo do pedido de oração.

        Returns:
            bool: True se o pedido foi adicionado com sucesso, False caso contrário.
        """
        try:
            workbook = openpyxl.load_workbook(self.arquivo_excel)
            folha = workbook.active
            dados = [timestamp, autor, conteudo]
            folha.append(dados)
            workbook.save(self.arquivo_excel)
            return True
        except Exception as e:
            print(f"Erro ao adicionar pedido de oração ao Excel local: {e}")
            return False


def criar_arquivo_credenciais_exemplo():
    """
    Cria um arquivo de exemplo para mostrar a estrutura das credenciais da conta de serviço.
    Este arquivo deve ser substituído pelas credenciais reais obtidas do Google Cloud Console.
    """
    exemplo = {
        "type": "service_account",
        "project_id": "seu-projeto-id",
        "private_key_id": "chave-privada-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nSua chave privada aqui\n-----END PRIVATE KEY-----\n",
        "client_email": "nome-da-conta@seu-projeto-id.iam.gserviceaccount.com",
        "client_id": "id-do-cliente",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/nome-da-conta%40seu-projeto-id.iam.gserviceaccount.com"
    }

    with open('service_account_exemplo.json', 'w') as f:
        json.dump(exemplo, f, indent=2)

    print("Arquivo de exemplo de credenciais criado: service_account_exemplo.json")
    print("Substitua este arquivo pelo arquivo de credenciais real obtido do Google Cloud Console.")


def main():
    """
    Função principal para demonstrar a integração com o Google Sheets.
    """
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"Arquivo de credenciais não encontrado: {SERVICE_ACCOUNT_FILE}")
        print("Criando arquivo de exemplo...")
        criar_arquivo_credenciais_exemplo()
        return

    try:
        sheets = GoogleSheetsIntegration()

        opcao = input(
            "Deseja criar uma nova planilha (N) ou usar uma existente (E)? ").strip().upper()

        if opcao == 'N':
            # Criar nova planilha
            titulo = input("Digite o título para a nova planilha: ").strip()
            planilha = sheets.criar_planilha(titulo)

            compartilhar = input(
                "Deseja compartilhar a planilha? (S/N) ").strip().upper()
            if compartilhar == 'S':
                email = input("Digite o e-mail para compartilhar: ").strip()
                role = input(
                    "Digite o papel (reader, writer, owner): ").strip().lower()
                sheets.compartilhar_planilha(planilha, email, role)

        else:
            # Usar planilha existente
            identificador = input(
                "Digite o título, URL ou ID da planilha: ").strip()
            planilha = sheets.abrir_planilha(identificador)

            if not planilha:
                print(
                    "Não foi possível abrir a planilha. Verifique o identificador e tente novamente.")
                return

        print("\nAdicionando um pedido de oração de exemplo...")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        autor = "Usuário de Exemplo"
        conteudo = "Peço oração pela saúde da família"
        conteudoOriginal = "Oração pela saúde da família"
        probabilidade = "Alta"

        if sheets.adicionar_pedido_oracao(planilha, timestamp, autor, conteudo, conteudoOriginal, probabilidade):
            print("Pedido de oração adicionado com sucesso!")

        print("\nPedidos de oração na planilha:")
        pedidos = sheets.obter_todos_pedidos(planilha)

        for i, pedido in enumerate(pedidos, 1):
            print(
                f"{i}. {pedido['Data/Hora']} - {pedido['Autor da Mensagem']}: {pedido['Pedido de Oração']}")

    except Exception as e:
        print(f"Erro na execução: {e}")


if __name__ == "__main__":
    main()
