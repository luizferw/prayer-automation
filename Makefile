# Variáveis
PYTHON = python3
PIP = pip3
MAIN = src/main.py
TESTS = tests/
LOGS = logs/
SECRETS = secrets/
REQUIREMENTS = requirements.txt

# Comandos
.PHONY: run
run:
	PYTHONPATH=src $(PYTHON) $(MAIN)

.PHONY: test
test:
	@$(PYTHON) -m unittest discover $(TESTS)

.PHONY: install
install:
	@$(PIP) install -r $(REQUIREMENTS)

.PHONY: clean
clean:
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@rm -rf $(LOGS)*

.PHONY: setup
setup:
	@bash install.sh

.PHONY: gui
gui:
	@$(PYTHON) src/gui/prayer_automation_gui.py

.PHONY: lint
lint:
	@$(PYTHON) -m flake8 src/ tests/

.PHONY: format
format:
	@$(PYTHON) -m black src/ tests/

.PHONY: secrets
secrets:
	@ls $(SECRETS)

.PHONY: help
help:
	@echo "Comandos disponíveis:"
	@echo "  run        - Executa o programa principal"
	@echo "  test       - Executa os testes"
	@echo "  install    - Instala as dependências"
	@echo "  clean      - Remove arquivos temporários e logs"
	@echo "  setup      - Configura o ambiente com o script install.sh"
	@echo "  gui        - Executa a interface gráfica"
	@echo "  lint       - Verifica o código com flake8"
	@echo "  format     - Formata o código com black"
	@echo "  secrets    - Lista os arquivos de credenciais"
	@echo "  help       - Mostra esta mensagem de ajuda"