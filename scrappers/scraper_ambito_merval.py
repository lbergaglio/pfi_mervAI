import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pickle
import logging

URL = "https://www.ambito.com/finanzas/"
COOKIES_PATH = "cookies.pkl"
TIME_SLEEP = 5


# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        logging.info(f"🍪 {len(cookies)} cookies cargadas correctamente desde {path}.")
    except FileNotFoundError:
        logging.warning(f"⚠️ El archivo de cookies no se encontró en '{path}'. Se continuará sin cookies.")
    except Exception as e:
        logging.error(f"⚠️ No se pudieron cargar las cookies desde '{path}': {e}")

def scrapear_ambito():
    edge_options = Options()
    edge_options.add_argument("--start-maximized")
    # Es mejor no hardcodear la ruta al driver, Selenium puede manejarlo si está en el PATH
    service = Service() 
    driver = webdriver.Edge(service=service, options=edge_options)

    driver.get(URL)
    time.sleep(TIME_SLEEP)

    cargar_cookies(driver)
    driver.refresh()
    time.sleep(TIME_SLEEP)

    articles = driver.find_elements(By.CSS_SELECTOR, "article a[href*='/finanzas/']")
    links = []

    for article in articles:
        href = article.get_attribute("href")
        if href and href not in links:
            links.append(href)

    links = links[:8]
    noticias = []

    for url in links:
        logging.info(f"🔗 Entrando a: {url}")
        try:
            driver.get(url)
            time.sleep(TIME_SLEEP)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(TIME_SLEEP)

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
            logging.info(f"🗞️ Noticia obtenida: {titulo}")
            # print(f"🗞️ {fecha} | {tags}")
            # print(f"📌 {titulo}")
            # print(f"🔗 {url}")
            # print(f"🏷️ Categorías: {categorias}")
            # print(f"📝 {contenido[:250]}...\n" + "-" * 120)

        except (NoSuchElementException, TimeoutException) as e:
            logging.warning(f"No se pudo encontrar un elemento en {url} o el tiempo de espera se agotó. Error: {type(e).__name__}")
        except Exception as e:
            logging.error(f"Error inesperado al procesar la nota {url}: {e}", exc_info=True)

    with open("noticias_ambito.json", "w", encoding="utf-8") as f:
        json.dump(noticias, f, indent=2, ensure_ascii=False)
        logging.info(f"\n💾 {len(noticias)} noticias guardadas en noticias_ambito.json")

    driver.quit()

if __name__ == "__main__":
    scrapear_ambito()
