from prayer_automation import PrayerRequestAutomation
import argparse
import logging
import os
import sys
from logger_config import logger

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    """
    Função principal para executar o sistema de automação.
    """
    parser = argparse.ArgumentParser(
        description='Automação para captura de pedidos de oração do YouTube')
    parser.add_argument(
        '--youtube-credentials',
        default='secrets/client_secret.json',
        help='Arquivo de credenciais do YouTube (padrão: client_secret.json)'
    )
    parser.add_argument(
        '--sheets-credentials',
        default='secrets/service_account.json',
        help='Arquivo de credenciais do Google Sheets (padrão: service_account.json)'
    )
    parser.add_argument(
        '--video-id',
        help='ID do vídeo do YouTube para monitorar'
    )
    parser.add_argument(
        '--planilha',
        help='Título, URL ou ID da planilha existente'
    )
    parser.add_argument(
        '--intervalo',
        type=int,
        default=10,
        help='Intervalo mínimo em segundos entre atualizações (padrão: 10)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Ativar modo de depuração'
    )
    parser.add_argument(
        '--local-excel',
        type=bool,
        default=False,
        help='Usar arquivo Excel local em vez do Google Sheets'
    )

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    base_dir = os.path.dirname(os.path.abspath(__file__))

    project_root = os.path.abspath(base_dir)
    youtube_credentials_path = os.path.join(
        project_root, args.youtube_credentials
    )
    sheets_credentials_path = os.path.join(
        project_root, args.sheets_credentials
    )

    print(f"Arquivo de credenciais do YouTube: {youtube_credentials_path}")

    if not os.path.exists(youtube_credentials_path):
        logger.error(
            f"Arquivo de credenciais do YouTube não encontrado: {youtube_credentials_path}")
        return

    if not os.path.exists(sheets_credentials_path):
        logger.error(
            f"Arquivo de credenciais do Google Sheets não encontrado: {sheets_credentials_path}")
        return

    print(f"Arquivo de credenciais do YouTube: {youtube_credentials_path}")

    automacao = PrayerRequestAutomation(
        youtube_credentials_path,
        sheets_credentials_path,
        use_local_excel=args.local_excel
    )

    if not automacao.inicializar():
        logger.error("Falha na inicialização do sistema de automação.")
        return

    if not automacao.configurar_planilha(args.planilha):
        logger.error("Falha na configuração da planilha.")
        return

    if not automacao.configurar_chat(args.video_id):
        logger.error("Falha na configuração do chat ao vivo.")
        return

    automacao.iniciar_monitoramento(args.intervalo)


if __name__ == "__main__":
    main()
