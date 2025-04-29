# Documentação do Sistema de Automação para Captura de Pedidos de Oração do YouTube

## Visão Geral

Este sistema automatiza a captura de pedidos de oração enviados no chat ao vivo do YouTube durante cultos religiosos e os adiciona a uma planilha do Google Sheets. O sistema utiliza a API do YouTube para monitorar mensagens do chat ao vivo, identifica pedidos de oração usando um algoritmo de detecção baseado em palavras-chave e padrões, e registra esses pedidos em uma planilha online para acompanhamento.

## Componentes do Sistema

O sistema é composto por três componentes principais:

1. **Monitoramento do Chat do YouTube** (`youtube_chat_monitor.py`): Conecta-se à API do YouTube para acessar mensagens do chat ao vivo e implementa o algoritmo de detecção de pedidos de oração.

2. **Integração com Google Sheets** (`google_sheets_integration.py`): Gerencia a conexão com o Google Sheets, permitindo criar planilhas, adicionar dados e compartilhar com outros usuários.

3. **Sistema de Automação Completo** (`prayer_automation.py`): Integra os dois componentes anteriores em um sistema unificado com interface de linha de comando.

## Requisitos

### Requisitos de Sistema

- Python 3.8 ou superior
- Acesso à internet
- Conta do Google com acesso ao YouTube e Google Sheets

### Bibliotecas Python Necessárias

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
gspread
```

## Configuração

### 1. Configurar Credenciais do YouTube

Para acessar a API do YouTube, você precisa criar credenciais OAuth:

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a API do YouTube Data v3
4. Configure a tela de consentimento OAuth
5. Crie credenciais OAuth 2.0 para aplicativo desktop
6. Baixe o arquivo JSON de credenciais e salve como `client_secret.json` na pasta do projeto

### 2. Configurar Credenciais do Google Sheets

Para acessar a API do Google Sheets, você precisa criar uma conta de serviço:

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. No mesmo projeto usado para o YouTube, vá para "IAM e administração" > "Contas de serviço"
3. Crie uma nova conta de serviço
4. Atribua o papel "Editor" à conta de serviço
5. Crie uma chave para a conta de serviço (formato JSON)
6. Baixe o arquivo JSON e salve como `service_account.json` na pasta do projeto

## Instalação

1. Clone ou baixe os arquivos do projeto para sua máquina local
2. Instale as dependências necessárias:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib gspread
```

3. Coloque os arquivos de credenciais (`client_secret.json` e `service_account.json`) na pasta raiz do projeto

## Uso

### Executando o Sistema Completo

O sistema completo pode ser executado através do script `prayer_automation.py`:

```bash
python3 ./src/main.py [opções]
```

#### Opções Disponíveis:

- `--youtube-credentials ARQUIVO`: Arquivo de credenciais do YouTube (padrão: client_secret.json)
- `--sheets-credentials ARQUIVO`: Arquivo de credenciais do Google Sheets (padrão: service_account.json)
- `--video-id ID`: ID do vídeo do YouTube para monitorar (opcional)
- `--planilha IDENTIFICADOR`: Título, URL ou ID da planilha existente (opcional)
- `--intervalo SEGUNDOS`: Intervalo mínimo em segundos entre atualizações (padrão: 10)
- `--debug`: Ativar modo de depuração

#### Exemplos:

**Monitorar a transmissão ao vivo atual e criar uma nova planilha:**
```bash
python3 ./src/main.py
```

**Monitorar um vídeo específico e usar uma planilha existente:**
```bash
python3 ./src/main.py --video-id dQw4w9WgXcQ --planilha "Pedidos de Oração"
```

**Usar configurações personalizadas:**
```bash
python3 ./src/main.py --youtube-credentials meu_cliente.json --sheets-credentials minha_conta.json --intervalo 20
```

### Primeira Execução

Na primeira execução, o sistema irá:

1. Solicitar autenticação no YouTube (abrirá um navegador para você fazer login)
2. Criar uma nova planilha do Google Sheets (se não for especificada uma existente)
3. Iniciar o monitoramento do chat ao vivo

### Monitoramento Contínuo

Uma vez iniciado, o sistema:

1. Monitora continuamente as mensagens do chat ao vivo
2. Detecta automaticamente pedidos de oração
3. Adiciona os pedidos à planilha do Google Sheets
4. Registra atividades no arquivo de log `prayer_automation.log`

Para interromper o monitoramento, pressione `Ctrl+C`.

## Algoritmo de Detecção de Pedidos de Oração

O algoritmo utiliza uma combinação de técnicas para identificar pedidos de oração:

1. **Detecção baseada em palavras-chave**: Identifica mensagens que contêm termos específicos relacionados a pedidos de oração
2. **Análise de padrões**: Reconhece estruturas comuns de frases usadas para pedidos de oração
3. **Sistema de pontuação**: Atribui pontos com base na presença de termos e padrões específicos

O algoritmo está configurado para detectar pedidos de oração em português. As palavras-chave incluem termos como "ore por", "peço oração", "intercedam por", entre outros.

## Personalização

### Ajustando o Algoritmo de Detecção

Para ajustar o algoritmo de detecção, você pode modificar as listas de termos no arquivo `youtube_chat_monitor.py`:

- `TERMOS_PRIMARIOS`: Termos com alta probabilidade de indicar um pedido de oração
- `TERMOS_SECUNDARIOS`: Termos com probabilidade média
- `TERMOS_CONTEXTUAIS`: Termos que reforçam a probabilidade quando combinados com outros
- `PADROES`: Expressões regulares para identificar padrões de pedidos de oração

### Personalizando a Planilha

A planilha criada pelo sistema tem uma estrutura padrão com as seguintes colunas:
- Data/Hora
- Autor da Mensagem
- Pedido de Oração

Para personalizar a estrutura da planilha, modifique o método `criar_planilha` no arquivo `google_sheets_integration.py`.

## Solução de Problemas

### Problemas Comuns

1. **Erro de autenticação do YouTube**:
   - Verifique se o arquivo `client_secret.json` está correto
   - Certifique-se de que a API do YouTube Data v3 está ativada no projeto
   - Tente excluir o arquivo `token.json` (se existir) e autenticar novamente

2. **Erro de autenticação do Google Sheets**:
   - Verifique se o arquivo `service_account.json` está correto
   - Certifique-se de que a conta de serviço tem permissões adequadas

3. **Chat ao vivo não encontrado**:
   - Verifique se o vídeo especificado é uma transmissão ao vivo
   - Certifique-se de que o chat ao vivo está ativado para a transmissão
   - Verifique se você tem permissão para acessar o chat

4. **Pedidos de oração não detectados**:
   - Ajuste os termos e padrões no algoritmo de detecção
   - Verifique o nível de pontuação necessário para classificar como pedido

### Logs

O sistema gera logs detalhados no arquivo `prayer_automation.log`. Consulte este arquivo para diagnosticar problemas.

Para logs mais detalhados, execute o sistema com a opção `--debug`.

## Testes

O sistema inclui testes unitários para validar seu funcionamento. Para executar os testes:

```bash
python3 ./tests/test_prayer_automation.py
```

## Limitações

- O sistema depende das APIs do YouTube e Google Sheets, que têm limites de cota
- A detecção de pedidos de oração é baseada em heurísticas e pode ter falsos positivos/negativos
- O sistema está otimizado para mensagens em português

## Próximos Passos

Possíveis melhorias futuras:

1. Interface gráfica para facilitar o uso
2. Suporte a múltiplos idiomas
3. Aprendizado de máquina para melhorar a detecção de pedidos
4. Notificações em tempo real para novos pedidos
5. Estatísticas e relatórios sobre os pedidos de oração

## Suporte

Para obter suporte ou relatar problemas, entre em contato com o desenvolvedor do sistema.

---

# Guia de Início Rápido

## Configuração em 5 Passos

1. **Instale as dependências**:
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib gspread
   ```

2. **Configure as credenciais do YouTube**:
   - Crie um projeto no [Google Cloud Console](https://console.cloud.google.com/)
   - Ative a API do YouTube Data v3
   - Crie credenciais OAuth 2.0 para aplicativo desktop
   - Baixe o arquivo JSON como `client_secret.json`

3. **Configure as credenciais do Google Sheets**:
   - No mesmo projeto, crie uma conta de serviço
   - Baixe a chave JSON como `service_account.json`

4. **Execute o sistema**:
   ```bash
   python3 ./src/main.py
   ```

5. **Autorize o acesso**:
   - Na primeira execução, um navegador abrirá para você autorizar o acesso ao YouTube
   - Faça login com sua conta do Google e conceda as permissões solicitadas

## Pronto!

O sistema agora está monitorando o chat ao vivo e adicionando pedidos de oração à planilha automaticamente.

Para interromper o monitoramento, pressione `Ctrl+C`.
