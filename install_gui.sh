if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller não está instalado. Instalando..."
    pip install pyinstaller
fi

# Cria o executável
pyinstaller --onefile --name prayer_automation \
    --add-data "client_secret.json:." \
    --add-data "service_account.json:." \
    --add-data "dados_chat.xlsx:." \
    prayer_automation_gui.py

# Move o executável para a pasta dist
echo "Executável criado na pasta dist/"
