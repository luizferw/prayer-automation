if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller não está instalado. Instalando..."
    pip install pyinstaller
fi

# Detecta o sistema operacional e cria o executável correspondente
OS_NAME=$(uname -s)
if [ "$OS_NAME" = "Linux" ]; then
    echo "Criando executável para Linux..."
    pyinstaller --onefile --windowed --noconsole --paths src src/gui/prayer_automation_gui.py --name prayer_automation_gui_linux
elif [[ "$OS_NAME" == MINGW* || "$OS_NAME" == CYGWIN* ]]; then
    echo "Criando executável para Windows..."
    pyinstaller --onefile --windowed --noconsole --paths src src/gui/prayer_automation_gui.py --name prayer_automation_gui_windows.exe
else
    echo "Sistema operacional não suportado."
    exit 1
fi

# Move o executável para a pasta dist
echo "Executável criado na pasta dist/"
