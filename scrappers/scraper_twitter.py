import os
import json
import time
import logging
import random
import subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Configuración
SCROLLS = 3
PAUSA = (10, 20)
TIEMPO_INICIAL = 15
KEYWORDS = ["argentina", "merval", "bono", "acción", "dólar", "bolsa", "riesgo país", "banco central", "inflación"]

# Cargar empresas
with open("empresas_merval_equivalencias.json", encoding="utf-8") as f:
    EMPRESAS = json.load(f)

# Log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Función para matar procesos previos
def matar_edge():
    logging.info("🧨 Cerrando Edge y msedgedriver previos…")
    subprocess.call("taskkill /f /im msedge.exe", shell=True, stderr=subprocess.DEVNULL)
    subprocess.call("taskkill /f /im msedgedriver.exe", shell=True, stderr=subprocess.DEVNULL)

# Bypass a detección de WebDriver
def configurar_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--user-data-dir=C:/Users/Luciano/AppData/Local/Microsoft/Edge/User Data")
    options.add_argument("--profile-directory=Profile 1")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """})
    
    return driver

# Lógica principal
def scrapear_tweets():
    matar_edge()
    driver = configurar_driver()
    tweets_finales = []

    for empresa in EMPRESAS:
        nombre = empresa
        query = f"{nombre} merval"
        url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"
        logging.info(f"🔎 Buscando: {query}")

        try:
            driver.get(url)
            time.sleep(TIEMPO_INICIAL)

            for i in range(SCROLLS):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(10,20))

            tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            logging.info(f"✍️ {len(tweets)} tweets encontrados para {nombre}")

            for tweet in tweets:
                try:
                    texto = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
                    autor = tweet.find_element(By.XPATH, './/div[@dir="ltr"]/span').text
                    link = tweet.find_element(By.XPATH, './/a[@role="link"]').get_attribute("href")

                    if any(palabra in texto.lower() for palabra in KEYWORDS):
                        tweets_finales.append({
                            "empresa": nombre,
                            "usuario": autor,
                            "contenido": texto,
                            "url": f"https://twitter.com{link}" if not link.startswith("http") else link,
                            "fecha_scrapeo": datetime.now().isoformat()
                        })

                except NoSuchElementException:
                    continue

        except Exception as e:
            logging.warning(f"⚠️ Fallo scrapeo para {nombre}: {e}")

    driver.quit()

    nombre_archivo = f"tweets_merval_selenium_{datetime.today().date()}.json"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(tweets_finales, f, indent=2, ensure_ascii=False)

    logging.info(f"✅ Se guardaron {len(tweets_finales)} tweets en {nombre_archivo}")

if __name__ == "__main__":
    scrapear_tweets()
