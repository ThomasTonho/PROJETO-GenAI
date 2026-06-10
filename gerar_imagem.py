import os
import re
import time
import argparse
import requests
from datetime import datetime

OUTPUT_DIR = "imagens_geradas"
API_URL = "https://aihorde.net/api/v2/generate/async"
MAX_ATTEMPTS = 60
POLL_INTERVAL = 10
DEFAULT_NEGATIVE = "blurry, deformed, bad anatomy, watermark, low quality, ugly, duplicate"


def sanitize_filename(text):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', text)[:30]


def download_image(url, prompt):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    filename = f"{sanitize_filename(prompt)}_{datetime.now().strftime('%d_%m_%H_%M')}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    with open(filepath, "wb") as f:
        f.write(response.content)

    print(f"Imagem salva: {filepath}")
    return filepath


def generate_image(prompt, negative=DEFAULT_NEGATIVE, nsfw=False):
    api_key = os.environ.get("AIHORDE_API_KEY", "0000000000")

    payload = {
        "prompt": f"{prompt} ### {negative}" if negative else prompt,
        "params": {
            "steps": 24,
            "cfg_scale": 7.5,
            "width": 1024,
            "height": 1024,
            "sampler_name": "k_dpmpp_2m",
        },
        "nsfw": nsfw,
        "trusted_workers": True,
        "models": ["Juggernaut XL"],
    }

    headers = {
        "Content-Type": "application/json",
        "apikey": api_key,
    }

    print("Enviando requisicao de geracao...")
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

    if response.status_code != 202:
        print(f"Falha na requisicao: status {response.status_code}")
        return None

    job_id = response.json().get("id")
    check_url = f"https://aihorde.net/api/v2/generate/check/{job_id}"
    status_url = f"https://aihorde.net/api/v2/generate/status/{job_id}"
    max_wait = MAX_ATTEMPTS * POLL_INTERVAL
    start = time.time()

    print("Aguardando geracao...")

    for _ in range(MAX_ATTEMPTS):
        time.sleep(POLL_INTERVAL)

        check = requests.get(check_url, timeout=30)
        if check.status_code != 200:
            continue

        if not check.json().get("done"):
            elapsed = int(time.time() - start)
            print(f"Processando... ({elapsed}s / ~{max_wait}s)")
            continue

        result = requests.get(status_url, timeout=30)
        if result.status_code != 200:
            print(f"Erro ao obter resultado: status {result.status_code}")
            return None

        generations = result.json().get("generations", [])
        if not generations:
            print("Nenhuma imagem retornada pela API.")
            return None

        image_url = generations[0].get("img")
        if not image_url:
            print("URL da imagem nao encontrada na resposta.")
            return None

        return download_image(image_url, prompt)

    print("Tempo esgotado aguardando geracao.")
    return None


def parse_args():
    parser = argparse.ArgumentParser(
        description="Gerador de imagens usando Juggernaut XL via AI Horde"
    )
    parser.add_argument("prompt", nargs="?", help="Descricao da imagem a ser gerada")
    parser.add_argument("--negative", default=DEFAULT_NEGATIVE, help="Elementos a evitar na imagem")
    parser.add_argument("--nsfw", action="store_true", help="Permite conteudo adulto")
    return parser.parse_args()


def main():
    args = parse_args()

    prompt = args.prompt or input("Digite o prompt: ").strip()
    if not prompt:
        print("Erro: o prompt nao pode estar vazio.")
        return

    print(f"Prompt  : {prompt}")
    print(f"Negativo: {args.negative}")

    result = generate_image(prompt, negative=args.negative, nsfw=args.nsfw)

    if result:
        print(f"Concluido. Imagem salva em: {result}")
    else:
        print("Falha na geracao da imagem.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcesso interrompido pelo usuario.")
