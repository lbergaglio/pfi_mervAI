from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import json
import time
import random
from datetime import datetime
import logging

# === Configuración ===
TWITTER_QUERY = "merval"
URL_BASE = f"https://twitter.com/search?q={TWITTER_QUERY}"
TIME_SLEEP = 5
SCROLLS = 5
KEYWORDS_ARG = [
    "argentina", "argentino", "merval", "banco central",
    "inflación", "dólar", "afip", "anses", "bonos",
    "renta fija", "bolsa", "finanzas", "reservas"
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def es_argentino(texto):
    texto = texto.lower()
    for k in KEYWORDS_ARG:
        palabras = texto.split()
        if any(k == palabra.strip('.,;:!¡¿?"\'') for palabra in palabras):
            return True
    return False

def scrapear_twitter():
    edge_options = Options()
    edge_options.add_argument("--start-maximized")
    edge_options.add_argument("--user-data-dir=C:/Users/Luciano/AppData/Local/Microsoft/Edge/User Data")
    edge_options.add_argument("--profile-directory=Profile 1")

    # Opcional: Solución para el error DevToolsActivePort
    edge_options.add_argument("--remote-debugging-port=9222")
    edge_options.add_experimental_option("detach", True)  # Mantiene abierto para depurar

    driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=edge_options)

    logging.info(f"🔍 Buscando en: {URL_BASE}")
    driver.get(URL_BASE)
    time.sleep(TIME_SLEEP)

    # Scroll para cargar más tuits
    for i in range(SCROLLS):
        logging.info(f"🔄 Scroll {i+1}/{SCROLLS}")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))

    tweets_data = []
    tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')

    logging.info(f"🧵 {len(tweets)} tuits encontrados.")

    for tweet in tweets:
        try:
            contenido = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
            usuario = tweet.find_element(By.XPATH, './/div[@dir="ltr"]/span').text
            enlace = tweet.find_element(By.XPATH, './/a[@role="link"]').get_attribute("href")
            fecha_scrapeo = datetime.now().isoformat()

            if es_argentino(contenido):
                tweet_dict = {
                    "fecha_scrapeo": fecha_scrapeo,
                    "usuario": usuario,
                    "contenido": contenido,
                    "url": f"https://twitter.com{enlace}" if not enlace.startswith("http") else enlace
                }
                tweets_data.append(tweet_dict)
                logging.info(f"📝 @{usuario}: {contenido[:80]}...")

        except (NoSuchElementException, TimeoutException):
            logging.warning("❌ Elemento no encontrado en un tuit.")
        except Exception as e:
            logging.error(f"⚠️ Error inesperado: {e}")

    driver.quit()

    # Guardar archivo JSON
    fecha_archivo = datetime.now().date()
    archivo = f"tweets_merval_{fecha_archivo}.json"
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(tweets_data, f, indent=2, ensure_ascii=False)
    logging.info(f"💾 {len(tweets_data)} tuits guardados en {archivo}")

if __name__ == "__main__":
    scrapear_twitter()
