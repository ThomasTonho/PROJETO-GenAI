# Gerador de Imagens com IA

Gerador de imagens a partir de texto usando a [AI Horde](https://aihorde.net/), uma plataforma distribuida e gratuita com modelos como o **Juggernaut XL**.

## Como funciona

O script envia um prompt de texto para a API da AI Horde, aguarda a geracao assincrona e salva a imagem resultante na pasta `imagens_geradas/`.

## Requisitos

- Python 3.8+

```bash
pip install -r requirements.txt
```

## Como usar

**Modo interativo:**
```bash
python gerar_imagem.py
```

**Passando o prompt direto:**
```bash
python gerar_imagem.py "a cat in space, cinematic lighting"
```

**Com negative prompt personalizado:**
```bash
python gerar_imagem.py "a cat in space" --negative "blurry, cartoon, low quality"
```

**Com conteudo adulto habilitado:**
```bash
python gerar_imagem.py "seu prompt" --nsfw
```

## Configuracao

Por padrao, o script usa a chave anonima da AI Horde (prioridade baixa na fila). Para usar sua propria chave e ter prioridade maior, crie uma conta em [aihorde.net](https://aihorde.net/) e defina a variavel de ambiente:

```bash
export AIHORDE_API_KEY="sua_chave_aqui"
python gerar_imagem.py "seu prompt"
```

## Exemplos de prompts

```
a futuristic city at sunset, ultra detailed, photorealistic
a cat cooking pasta in a cozy kitchen, digital art
portrait of a samurai warrior in the rain, cinematic lighting
```

## Modelo utilizado

**Juggernaut XL** — modelo de alta qualidade para geracao fotorrealista e artistica.
