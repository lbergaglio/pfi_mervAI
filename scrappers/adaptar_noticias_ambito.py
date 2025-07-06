import json
import requests

NIVEL = "basico"  # Cambia el nivel si lo deseas
API_URL = "http://localhost:5001/api/adaptar-texto"

with open("noticias_ambito.json", "r", encoding="utf-8") as f:
    noticias = json.load(f)

noticias_adaptadas = []

for noticia in noticias:
    texto_original = noticia.get("contenido", "")
    if not texto_original.strip():
        noticia["contenido_adaptado"] = ""
        continue
    payload = {"texto": texto_original, "nivel": NIVEL}
    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        if response.status_code == 200:
            adaptado = response.json().get("adaptado", "")
            noticia["contenido_adaptado"] = adaptado
            print(f"✅ Adaptado: {noticia.get('titulo', '')[:60]}...")
        else:
            noticia["contenido_adaptado"] = "[ERROR EN API]"
            print(f"❌ Error adaptando: {noticia.get('titulo', '')[:60]}... Código: {response.status_code}")
    except Exception as e:
        noticia["contenido_adaptado"] = f"[ERROR: {e} ]"
        print(f"❌ Excepción adaptando: {noticia.get('titulo', '')[:60]}... {e}")
    noticias_adaptadas.append(noticia)

with open("noticias_ambito_adaptadas.json", "w", encoding="utf-8") as f:
    json.dump(noticias_adaptadas, f, indent=2, ensure_ascii=False)
    print("\n💾 Noticias adaptadas guardadas en noticias_ambito_adaptadas.json")
