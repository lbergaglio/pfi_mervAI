from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import json
import time
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
stopwords_es = stopwords.words('spanish')

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

def clasificar_noticias(noticias):
    textos = [n["contenido"] for n in noticias if n["contenido"].strip()]
    if len(textos) < 2:
        print("⚠️ No hay suficientes noticias para clasificar.")
        return noticias

    vectorizer = TfidfVectorizer(stop_words=stopwords_es)
    X = vectorizer.fit_transform(textos)

    n_clusters = min(4, len(noticias))
    model = KMeans(n_clusters=n_clusters, random_state=0, n_init="auto")
    y = model.fit_predict(X)

    for i, n in enumerate(noticias):
        n["categoria"] = f"cluster_{y[i]}" if i < len(y) else "sin_cluster"

    return noticias

def scrapear_infobae_selenium():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.infobae.com/economia/finanzas-y-negocios/")
    time.sleep(3)

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

        print(f"🔗 Probando URL: {href}")
        try:
            driver.get(href)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.article-body, div[itemprop='articleBody'], article"))
            )
            art_soup = BeautifulSoup(driver.page_source, "html.parser")

            # Varios posibles selectores para adaptarnos a variaciones
            cuerpo = (
                art_soup.select_one("div.article-body") or 
                art_soup.select_one("div[itemprop='articleBody']") or
                art_soup.select_one("article")
            )

            if not cuerpo:
                print("⚠️ Cuerpo no encontrado.")
                continue

            parrafos = cuerpo.find_all("p")
            texto = "\n".join(p.get_text(strip=True) for p in parrafos if p.get_text(strip=True))
            if len(texto.strip()) < 100:
                print("⚠️ Contenido vacío o muy corto.")
                continue

            noticia = {
                "titulo": titulo,
                "link": href,
                "fecha": datetime.now().isoformat(),
                "contenido": texto,
                "tags": detectar_activos(titulo)
            }
            noticias.append(noticia)

        except Exception as e:
            print(f"⚠️ Error procesando {href}: {e}")
            continue

    driver.quit()

    if not noticias:
        print("⚠️ No se encontró ninguna noticia válida.")
        return []

    noticias = clasificar_noticias(noticias)

    with open("noticias_infobae.json", "w", encoding="utf-8") as f:
        json.dump(noticias, f, indent=2, ensure_ascii=False)
    print(f"\n💾 {len(noticias)} noticias guardadas en noticias_infobae.json")

    return noticias

if __name__ == "__main__":
    noticias = scrapear_infobae_selenium()
    for i, n in enumerate(noticias, start=1):
        print(f"\n📰 Noticia #{i}")
        print(f"📅 Fecha: {n['fecha']}")
        print(f"🏷️ Tags: {', '.join(n['tags'])}")
        print(f"📂 Categoría: {n['categoria']}")
        print(f"🧾 Título: {n['titulo']}")
        print(f"🔗 Link: {n['link']}")
        print(f"📄 Contenido:\n{n['contenido'][:800]}...")
        print("-" * 80)
