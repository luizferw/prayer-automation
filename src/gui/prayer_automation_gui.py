#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface Gráfica para o Sistema de Automação de Pedidos de Oração
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import os
import threading
from prayer_automation import PrayerRequestAutomation


class PrayerAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Automação de Pedidos de Oração")

        # Variáveis
        self.youtube_credentials = tk.StringVar(
            value="src/secrets/client_secret.json")
        self.sheets_credentials = tk.StringVar(
            value="src/secrets/service_account.json")
        self.video_id = tk.StringVar()
        self.planilha = tk.StringVar()
        self.intervalo = tk.IntVar(value=10)
        self.debug = tk.BooleanVar(value=False)

        # Layout
        self.create_widgets()

    def create_widgets(self):
        # Credenciais do YouTube
        tk.Label(self.root, text="Credenciais do YouTube:").grid(
            row=0, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.youtube_credentials,
                 width=50).grid(row=0, column=1)
        tk.Button(self.root, text="Selecionar",
                  command=self.select_youtube_credentials).grid(row=0, column=2)

        # Credenciais do Google Sheets
        tk.Label(self.root, text="Credenciais do Google Sheets:").grid(
            row=1, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.sheets_credentials,
                 width=50).grid(row=1, column=1)
        tk.Button(self.root, text="Selecionar",
                  command=self.select_sheets_credentials).grid(row=1, column=2)

        # ID do Vídeo
        tk.Label(self.root, text="ID do Vídeo:").grid(
            row=2, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.video_id,
                 width=50).grid(row=2, column=1)

        # Planilha
        tk.Label(self.root, text="Planilha:").grid(
            row=3, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.planilha,
                 width=50).grid(row=3, column=1)

        # Debug
        tk.Checkbutton(self.root, text="Modo Debug", variable=self.debug).grid(
            row=5, column=0, sticky="w")

        # Botões
        tk.Button(self.root, text="Iniciar", command=self.start_automation).grid(
            row=6, column=0, pady=10)
        tk.Button(self.root, text="Sair", command=self.root.quit).grid(
            row=6, column=1, pady=10)

    def select_youtube_credentials(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")])
        if filepath:
            self.youtube_credentials.set(filepath)

    def select_sheets_credentials(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")])
        if filepath:
            self.sheets_credentials.set(filepath)

    def start_automation(self):
        youtube_credentials = self.youtube_credentials.get()
        sheets_credentials = self.sheets_credentials.get()
        video_id = self.video_id.get()
        planilha = self.planilha.get()
        intervalo = self.intervalo.get()
        debug = self.debug.get()

        if not os.path.exists(youtube_credentials):
            messagebox.showerror(
                "Erro", "Arquivo de credenciais do YouTube não encontrado.")
            return

        if not os.path.exists(sheets_credentials):
            messagebox.showerror(
                "Erro", "Arquivo de credenciais do Google Sheets não encontrado.")
            return

        if not video_id:
            messagebox.showerror(
                "Erro", "O ID do vídeo é obrigatório para iniciar a automação.")
            return

        def run_automation():
            try:
                automacao = PrayerRequestAutomation(
                    youtube_credentials, sheets_credentials)
                if not automacao.inicializar():
                    raise Exception(
                        "Falha na inicialização do sistema de automação.")

                if not automacao.configurar_planilha(planilha):
                    raise Exception("Falha na configuração da planilha.")

                if not automacao.configurar_chat(video_id):
                    raise Exception("Falha na configuração do chat ao vivo.")

                automacao.iniciar_monitoramento(intervalo)
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        threading.Thread(target=run_automation, daemon=True).start()
        messagebox.showinfo(
            "Automação", "Monitoramento iniciado. Consulte os logs para mais detalhes.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PrayerAutomationGUI(root)
    root.mainloop()
