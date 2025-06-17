import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Lista de activos del MERVAL a detectar
ACTIVOS = [
    "YPF", "GGAL", "ALUA", "PAMP", "BMA", "SUPV", "CEPU", "TXAR", "MIRG", "COME",
    "EDN", "TRAN", "TS", "TGSU2", "VALO", "BYMA", "HARG", "IRSA", "LOMA", "TGNO4"
]

def detectar_activos(texto):
    texto_mayus = texto.upper()
    encontrados = [activo for activo in texto_mayus.split() if activo in ACTIVOS]
    return encontrados if encontrados else ["MERVAL"]

def es_noticia_argentina(texto):
    keywords = [
        "argentina", "argentino", "buenos aires", "inflación", "dólar", "banco central",
        "economía local", "gobierno", "mercado argentino", "AFIP", "ANSES", "Merval", "BCRA"
    ]
    texto_lower = texto.lower()
    return any(palabra in texto_lower for palabra in keywords)


def scrapear_ambito():
    url = "https://www.ambito.com/finanzas"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    noticias = []
    articulos = soup.find_all("article")

    for art in articulos:
        titulo_tag = art.find("h2") or art.find("h3") or art.find("h4")
        if not titulo_tag:
            continue

        titulo = titulo_tag.get_text(strip=True)
        if not es_noticia_argentina(titulo):
            continue
        link_tag = art.find("a")
        link = link_tag["href"] if link_tag and "href" in link_tag.attrs else ""
        if link and not link.startswith("http"):
            link = "https://www.ambito.com" + link

        activos = detectar_activos(titulo)

        noticia = {
            "titulo": titulo,
            "link": link,
            "fuente": "Ámbito",
            "fecha": datetime.now().isoformat(),
            "contenido": None,
            "sentimiento": None,
            "tags": activos
        }

        noticias.append(noticia)

    return noticias

if __name__ == "__main__":
    noticias = scrapear_ambito()
    for i, n in enumerate(noticias, 1):
        print(f"📰 Noticia #{i}")
        print(f"📅 Fecha: {n['fecha']}")
        print(f"🏷️ Tags: {', '.join(n['tags'])}")
        print(f"🧾 Título: {n['titulo']}")
        print(f"🔗 Link: {n['link']}")
        print("-" * 80)

