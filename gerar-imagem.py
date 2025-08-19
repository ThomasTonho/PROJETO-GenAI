import requests
import re
import time
from datetime import datetime

def limpar_nome(texto):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', texto)[:30]

def salvar_imagem_da_url(url, texto):
    try:
        prompt_seguro = limpar_nome(texto)
        carimbo_tempo = datetime.now().strftime('%d_%m_%H_%M')
        nome_arquivo = f"{prompt_seguro}_{carimbo_tempo}.png"

        resposta = requests.get(url, timeout=60)
        resposta.raise_for_status()

        with open(nome_arquivo, "wb") as arquivo:
            arquivo.write(resposta.content)

        print(f"⬆️  Salva como {nome_arquivo}")
        return nome_arquivo
    except requests.exceptions.RequestException as erro:
        print(f"❌ Erro ao baixar a imagem: {erro}")
        return None
    except IOError as erro:
        print(f"❌ Erro ao salvar a imagem: {erro}")
        return None

def gerar_imagem_com_juggernaut(texto):
    try:
        print("🔄 Gerando imagem")
        
        URL_API = "https://aihorde.net/api/v2/generate/async"
        
        dados = {
            "prompt": texto,
            "params": {
                "steps": 24,
                "cfg_scale": 7.5,
                "width": 1024,
                "height": 1024,
                "sampler_name": "k_dpmpp_2m"
            },
            "nsfw": True,
            "trusted_workers": True,
            "models": ["Juggernaut XL"]
        }
        
        cabecalhos = {
            "Content-Type": "application/json",
            "apikey": "0000000000" 
        }
        
        print("📤 Gerando imagem...")
        resposta = requests.post(URL_API, headers=cabecalhos, json=dados, timeout=30)
        
        if resposta.status_code == 202:
            id_trabalho = resposta.json().get("id")
            print("⏳ Aguardando geração da imagem...")
            
            url_verificacao = f"https://aihorde.net/api/v2/generate/check/{id_trabalho}"
            
            for tentativa in range(60): 
                time.sleep(10)
                resposta_verificacao = requests.get(url_verificacao, timeout=30)
                
                if resposta_verificacao.status_code == 200:
                    estado = resposta_verificacao.json()
                    if estado.get("done"):
                        print("✅ Imagem gerada!")
                        
                        url_resultado = f"https://aihorde.net/api/v2/generate/status/{id_trabalho}"
                        resposta_resultado = requests.get(url_resultado, timeout=30)
                        
                        if resposta_resultado.status_code == 200:
                            resultado = resposta_resultado.json()
                            if resultado.get("generations") and len(resultado["generations"]) > 0:
                                url_imagem = resultado["generations"][0].get("img")
                                if url_imagem:
                                    return salvar_imagem_da_url(url_imagem, texto)
                        break
                    else:
                        print(f"⏳ Aguardando... ({tentativa+1}/60)")
            
            print("❌ Tempo esgotado aguardando geração")
            return None
        else:
            print(f"❌ Erro ao submeter trabalho: {resposta.status_code}")
            return None
            
    except Exception as erro:
        print(f"❌ Erro na geração: {erro}")
        return None

def executar_aplicacao():
    try:
        print("🎨 GERADOR DE IMAGEM DO THOMAS - Usando Juggernaut XL")
        print("=" * 40)
        
        texto = input("Digite o prompt: ")
        if not texto.strip():
            print("❌ Erro: o prompt não pode estar vazio!")
            return

        print(f"📝 Prompt: {texto}")

        resultado = gerar_imagem_com_juggernaut(texto)
        
        if resultado:
            print("🎉 Processo concluído com sucesso!")
            print("📁 Verifique a pasta para encontrar sua imagem!")
        else:
            print("❌ Falha na geração da imagem.")
        
    except KeyboardInterrupt:
        print("⏹️  Processo interrompido pelo usuário")
    except Exception as erro:
        print(f"❌ Erro inesperado: {erro}")

if __name__ == "__main__":
    executar_aplicacao()
