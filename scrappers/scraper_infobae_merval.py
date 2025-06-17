from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time

ACTIVOS = ["YPF", "GGAL", "ALUA", "PAMP", "BMA", "SUPV", "CEPU",
           "TXAR", "MIRG", "COME", "EDN", "TRAN", "TS",
           "TGSU2", "VALO", "BYMA", "HARG", "IRSA", "LOMA", "TGNO4"]

KEYWORDS_ARG = ["argentina", "argentino", "merval", "banco central",
                "inflación", "dólar", "afip", "anses", "bonos",
                "renta fija", "bolsa", "finanzas"]

def detectar_activos(texto):
    upper = texto.upper()
    encontrados = [act for act in ACTIVOS if act in upper]
    return encontrados or ["MERVAL"]

def es_argentina(texto):
    lower = texto.lower()
    return any(k in lower for k in KEYWORDS_ARG)

def scrapear_infobae_selenium():
    options = Options()
    options.add_argument("--headless")  # Ejecutar sin ventana
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.infobae.com/economia/finanzas-y-negocios/")
    time.sleep(3)  # Esperar a que cargue el contenido

    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = soup.select("a[href*='/economia/finanzas-y-negocios/']")

    noticias = []
    vistos = set()

    for tag in links:
        titulo = tag.get_text(strip=True)
        href = tag.get("href", "")
        if not titulo or len(titulo) < 40:
            continue
        if href.startswith("/"):
            href = "https://www.infobae.com" + href
        if href in vistos:
            continue
        vistos.add(href)

        if not es_argentina(titulo):
            continue

        driver.get(href)
        time.sleep(2)
        art_soup = BeautifulSoup(driver.page_source, "html.parser")

        cuerpo = art_soup.select_one("div.article-body") or art_soup.select_one("div[itemprop='articleBody']")
        if not cuerpo:
            continue

        texto = "\n".join(p.get_text(strip=True) for p in cuerpo.find_all("p") if p.get_text(strip=True))

        noticia = {
            "titulo": titulo,
            "link": href,
            "fecha": datetime.now().isoformat(),
            "contenido": texto,
            "tags": detectar_activos(titulo)
        }
        noticias.append(noticia)

    driver.quit()
    return noticias

if __name__ == "__main__":
    for i, n in enumerate(scrapear_infobae_selenium(), start=1):
        print(f"📰 Noticia #{i}")
        print(f"📅 Fecha: {n['fecha']}")
        print(f"🏷️ Tags: {', '.join(n['tags'])}")
        print(f"🧾 Título: {n['titulo']}")
        print(f"🔗 Link: {n['link']}")
        print(f"📄 Contenido:\n{n['contenido'][:800]}...\n")
        print("-" * 80)
