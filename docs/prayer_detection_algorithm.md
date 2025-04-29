# Algoritmo para Detecção de Pedidos de Oração

## Visão Geral

Este documento descreve o algoritmo para detectar pedidos de oração em mensagens do chat ao vivo do YouTube durante cultos religiosos. O objetivo é identificar com precisão quais mensagens contêm pedidos de oração, extrair o nome da pessoa que precisa de oração (que pode ser o próprio autor da mensagem ou outra pessoa) e o conteúdo do pedido.

## Abordagem

O algoritmo utilizará uma combinação de técnicas:

1. **Detecção baseada em palavras-chave**: Identificar mensagens que contêm termos específicos relacionados a pedidos de oração
2. **Análise de padrões**: Reconhecer estruturas comuns de frases usadas para pedidos de oração
3. **Extração de informações**: Separar o nome da pessoa e o motivo/conteúdo do pedido

## Detecção baseada em palavras-chave

### Palavras e frases indicadoras de pedidos de oração

#### Termos primários (alta probabilidade)
- "ore por"
- "oração por"
- "orem por"
- "orar por"
- "peço oração"
- "pedido de oração"
- "por favor orem"
- "intercedam por"
- "intercessão por"

#### Termos secundários (probabilidade média)
- "preciso de oração"
- "necessito de oração"
- "por favor ore"
- "oração para"
- "ore pela"
- "ore pelo"
- "orem pela"
- "orem pelo"

#### Termos contextuais (reforçam a probabilidade quando combinados com outros)
- "saúde"
- "doença"
- "hospital"
- "cirurgia"
- "família"
- "problema"
- "dificuldade"
- "cura"
- "libertação"
- "restauração"
- "provisão"
- "financeiro"
- "emprego"
- "trabalho"

## Análise de Padrões

### Padrões comuns de pedidos de oração

1. **Padrão direto**: "Ore por [nome] que está [situação]"
   - Exemplo: "Ore por minha mãe que está no hospital"

2. **Padrão com introdução**: "Por favor, peço oração por [nome/situação]"
   - Exemplo: "Por favor, peço oração por meu filho que fará uma cirurgia"

3. **Padrão pessoal**: "Preciso de oração para [situação]"
   - Exemplo: "Preciso de oração para conseguir um emprego"

4. **Padrão simples**: "[Nome] + [situação] + oração"
   - Exemplo: "Maria com câncer, oração por favor"

5. **Padrão implícito**: Mensagem que descreve uma situação difícil sem pedir explicitamente oração
   - Exemplo: "Meu pai está internado em estado grave"

## Algoritmo de Detecção

### Fluxo de Processamento

1. **Pré-processamento da mensagem**:
   - Converter para minúsculas
   - Remover acentos
   - Normalizar espaços

2. **Pontuação inicial**:
   - Atribuir uma pontuação base de 0 a cada mensagem
   - Incrementar pontuação para cada termo primário encontrado (+3 pontos)
   - Incrementar pontuação para cada termo secundário encontrado (+2 pontos)
   - Incrementar pontuação para cada termo contextual encontrado (+1 ponto)

3. **Análise de padrões**:
   - Verificar se a mensagem segue algum dos padrões conhecidos
   - Incrementar pontuação com base no padrão identificado (+2 pontos)

4. **Decisão**:
   - Se pontuação ≥ 4: Classificar como pedido de oração
   - Se pontuação = 3: Classificar como possível pedido de oração (requer verificação adicional)
   - Se pontuação < 3: Não classificar como pedido de oração

### Extração de Informações

Para mensagens classificadas como pedidos de oração:

1. **Identificação do nome**:
   - Procurar por padrões como "ore por [nome]", "oração para [nome]"
   - Se não encontrar nome específico, assumir que o pedido é para o próprio autor da mensagem
   - Extrair o nome do autor da mensagem do campo `authorDetails.displayName`

2. **Extração do conteúdo do pedido**:
   - Remover as palavras-chave de pedido de oração
   - Remover o nome identificado
   - O texto restante é considerado o conteúdo do pedido

## Implementação

A implementação do algoritmo será feita em Python, utilizando técnicas de processamento de linguagem natural básicas:

```python
def detectar_pedido_oracao(mensagem, autor):
    # Pré-processamento
    texto = normalizar_texto(mensagem.lower())
    
    # Pontuação inicial
    pontuacao = 0
    
    # Verificar termos primários
    for termo in TERMOS_PRIMARIOS:
        if termo in texto:
            pontuacao += 3
    
    # Verificar termos secundários
    for termo in TERMOS_SECUNDARIOS:
        if termo in texto:
            pontuacao += 2
    
    # Verificar termos contextuais
    for termo in TERMOS_CONTEXTUAIS:
        if termo in texto:
            pontuacao += 1
    
    # Verificar padrões
    for padrao in PADROES:
        if re.search(padrao, texto):
            pontuacao += 2
            break
    
    # Decisão
    if pontuacao >= 4:
        # Extrair informações
        nome = extrair_nome(texto) or autor
        conteudo = extrair_conteudo(texto, nome)
        return True, nome, conteudo
    elif pontuacao == 3:
        # Possível pedido, mas incerto
        return "possivel", autor, texto
    else:
        # Não é um pedido de oração
        return False, None, None
```

## Melhorias Futuras

1. **Aprendizado de máquina**: Implementar um modelo de classificação treinado com exemplos reais de pedidos de oração
2. **Análise de sentimento**: Incorporar análise de sentimento para identificar mensagens com tom de súplica ou urgência
3. **Feedback do usuário**: Permitir que o operador do sistema forneça feedback sobre falsos positivos/negativos para melhorar o algoritmo
4. **Expansão de idiomas**: Adicionar suporte para detectar pedidos de oração em outros idiomas além do português

## Considerações Finais

Este algoritmo foi projetado para equilibrar precisão e recall, priorizando a captura da maioria dos pedidos de oração genuínos, mesmo que isso signifique alguns falsos positivos. Em um contexto religioso, é preferível incluir um pedido duvidoso do que ignorar um pedido genuíno.

O algoritmo será refinado durante a fase de testes com dados reais de chats ao vivo de cultos religiosos.
