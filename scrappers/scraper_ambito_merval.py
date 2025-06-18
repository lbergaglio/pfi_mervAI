import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import pickle

URL = "https://www.ambito.com/finanzas/"
COOKIES_PATH = "cookies.pkl"

# === Clasificación automática por palabras clave ===
CATEGORIAS = {
    "dólar": ["dólar", "dólares", "blue", "oficial", "mayorista", "MEP", "CCL"],
    "acciones": ["acción", "acciones", "ADR", "renta variable"],
    "bonos": ["bonos", "bono", "título", "deuda", "AL30", "GD30", "cupones"],
    "Merval": ["Merval", "índice", "bolsa porteña"],
    "macro": ["inflación", "actividad", "PIB", "economía", "recesión", "macroeconomía", "macroeconómico", "superávit"],
    "internacional": ["Wall Street", "EEUU", "China", "Brasil", "global", "internacional", "Reserva Federal", "Fed"]
}

def clasificar_texto(texto):
    texto = texto.lower()
    categorias_detectadas = []
    for categoria, palabras in CATEGORIAS.items():
        if any(palabra.lower() in texto for palabra in palabras):
            categorias_detectadas.append(categoria)
    return categorias_detectadas if categorias_detectadas else ["otras"]

def cargar_cookies(driver, path=COOKIES_PATH):
    try:
        with open(path, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print(f"🍪 {len(cookies)} cookies cargadas correctamente.")
    except Exception as e:
        print(f"⚠️ No se pudieron cargar cookies: {e}")

def scrapear_ambito():
    edge_options = Options()
    edge_options.add_argument("--start-maximized")

    service = Service("C:\\Users\\Luciano\\Desktop\\UADE\\PFI\\drivers\\msedgedriver.exe")
    driver = webdriver.Edge(service=service, options=edge_options)

    driver.get(URL)
    time.sleep(2)

    cargar_cookies(driver)
    driver.refresh()
    time.sleep(2)

    articles = driver.find_elements(By.CSS_SELECTOR, "article a[href*='/finanzas/']")
    links = []

    for article in articles:
        href = article.get_attribute("href")
        if href and href not in links:
            links.append(href)

    links = links[:8]
    noticias = []

    for url in links:
        print(f"\n🔗 Entrando a: {url}")
        try:
            driver.get(url)
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            titulo = driver.find_element(By.TAG_NAME, "h1").text

            contenido = ""
            posibles_selectores = [
                ".article-main-content",
                ".article-body",
                "div.article-content",
                "div.article-text"
            ]
            for selector in posibles_selectores:
                elementos = driver.find_elements(By.CSS_SELECTOR, f"{selector} p")
                if elementos:
                    contenido = "\n".join([el.text for el in elementos if el.text.strip()])
                    break

            if not contenido:
                contenido = "[Contenido no encontrado]"

            tags = [tag.text for tag in driver.find_elements(By.CSS_SELECTOR, ".tags a")]
            fecha = datetime.now().isoformat()

            if "Registrate gratis" in contenido or "superaste el límite" in contenido.lower():
                contenido = "[Bloqueado por muro de pago]"

            categorias = clasificar_texto(titulo + " " + contenido)

            noticia = {
                "fecha": fecha,
                "tags": tags,
                "titulo": titulo,
                "url": url,
                "contenido": contenido.strip(),
                "categorias": categorias
            }

            noticias.append(noticia)
            print(f"🗞️ {fecha} | {tags}")
            print(f"📌 {titulo}")
            print(f"🔗 {url}")
            print(f"🏷️ Categorías: {categorias}")
            print(f"📝 {contenido[:250]}...\n" + "-" * 120)

        except Exception as e:
            print(f"⚠️ Error al procesar la nota: {e}")

    with open("noticias_ambito.json", "w", encoding="utf-8") as f:
        json.dump(noticias, f, indent=2, ensure_ascii=False)
        print(f"\n💾 {len(noticias)} noticias guardadas en noticias_ambito.json")

    driver.quit()

if __name__ == "__main__":
    scrapear_ambito()
