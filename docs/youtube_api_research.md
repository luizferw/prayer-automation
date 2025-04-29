# Pesquisa sobre a API do YouTube para Monitoramento de Chat ao Vivo

## Visão Geral

A API do YouTube Live Streaming fornece recursos para acessar mensagens de chat ao vivo durante transmissões. Isso é essencial para nossa automação que precisa capturar pedidos de oração enviados no chat ao vivo.

## Recursos Principais

### LiveChatMessages

O recurso `liveChatMessage` representa uma mensagem no chat ao vivo do YouTube. Este recurso pode conter detalhes sobre vários tipos de mensagens, incluindo mensagens de texto recém-postadas.

- O chat ao vivo é ativado por padrão para transmissões ao vivo e está disponível enquanto o evento ao vivo estiver ativo.
- Após o término do evento, o chat ao vivo não está mais disponível para esse evento.

### Propriedades Importantes

- `id`: O ID que o YouTube atribui para identificar exclusivamente a mensagem.
- `snippet.type`: O tipo da mensagem (textMessageEvent, etc.).
- `snippet.liveChatId`: O ID que identifica exclusivamente o chat ao vivo com o qual a mensagem está associada.
- `snippet.authorChannelId`: O ID do usuário que escreveu a mensagem.
- `snippet.publishedAt`: A data e hora em que a mensagem foi originalmente publicada.
- `snippet.displayMessage`: Contém uma string que é exibida aos usuários.
- `snippet.textMessageDetails.messageText`: O texto da mensagem do usuário.
- `authorDetails.displayName`: O nome de exibição do autor da mensagem.

## Métodos da API

### list

O método `list` lista mensagens de chat ao vivo para um chat específico.

**Requisição HTTP:**
```
GET https://www.googleapis.com/youtube/v3/liveChat/messages
```

**Parâmetros Obrigatórios:**
- `liveChatId`: O ID do chat cujas mensagens serão retornadas.
- `part`: As partes do recurso `liveChatMessage` que a resposta da API incluirá. Valores suportados são `id`, `snippet` e `authorDetails`.

**Parâmetros Opcionais:**
- `maxResults`: O número máximo de mensagens que devem ser retornadas no conjunto de resultados (200-2000, padrão: 500).
- `pageToken`: Identifica uma página específica no conjunto de resultados que deve ser retornada.

**Resposta:**
A resposta inclui:
- `nextPageToken`: Token para a próxima página de resultados.
- `pollingIntervalMillis`: Tempo em milissegundos que o cliente deve aguardar antes de consultar novamente.
- `items`: Lista de mensagens, cada item é um recurso `liveChatMessage`.

## Fluxo de Trabalho para Acessar Mensagens do Chat ao Vivo

Com base na documentação e exemplos, o fluxo de trabalho para acessar mensagens do chat ao vivo é:

1. **Solicitar uma lista de eventos ao vivo**:
   ```
   https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=CHANNEL_ID&order=date&type=video&key=API_KEY
   ```
   - Procurar por itens onde `snippet.liveBroadcastContent` é "live"

2. **Usar o ID do vídeo ao vivo para solicitar detalhes da transmissão ao vivo**:
   ```
   https://www.googleapis.com/youtube/v3/videos?part=liveStreamingDetails&id=VIDEO_ID&key=API_KEY
   ```
   - Obter o `liveStreamingDetails.activeLiveChatId` da resposta

3. **Solicitar mensagens do chat ao vivo usando o activeLiveChatId**:
   ```
   https://www.googleapis.com/youtube/v3/liveChat/messages?part=snippet,authorDetails&liveChatId=ACTIVE_LIVE_CHAT_ID&key=API_KEY
   ```
   - Processar as mensagens retornadas
   - Usar o `nextPageToken` para obter mais mensagens
   - Respeitar o `pollingIntervalMillis` para determinar quando fazer a próxima solicitação

## Requisitos de Autenticação

- Todas as solicitações de API requerem uma chave de API do YouTube Data API (sem necessidade de OAuth, apenas uma chave de API).
- É necessário criar um projeto no Google Cloud Console e ativar a API do YouTube Data v3.
- A chave de API tem limites de cota diários.

## Considerações para Nossa Automação

1. Precisaremos monitorar continuamente o chat ao vivo durante os cultos.
2. Devemos implementar um mecanismo de polling que respeite o `pollingIntervalMillis` retornado pela API.
3. Precisamos analisar cada mensagem para determinar se é um pedido de oração.
4. Para cada pedido de oração identificado, extrairemos o nome do usuário e o conteúdo do pedido.
5. Esses dados serão então enviados para uma planilha do Google Sheets.

## Próximos Passos

- Pesquisar as capacidades da API do Google Sheets para integração com planilhas online.
- Projetar um algoritmo para detecção de pedidos de oração nas mensagens do chat.
