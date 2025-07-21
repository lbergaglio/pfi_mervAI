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
SCROLLS = 10
PAUSA = (10, 20)
TIEMPO_INICIAL = 15
KEYWORDS = ["argentina", "merval", "bono", "acción", "dólar", "bolsa", "riesgo país", "banco central", "inflación"]

# Lógica principal
def scrapear_tweets(empresa,driver):
    # Log
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    #empresa= "$YPF"
    #matar_edge()
    tweets_finales = []
    query = f"{empresa}"
    url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"
    
    logging.info(f"🔎 Buscando: {query}")

    try:
        driver.get(url)
        time.sleep(TIEMPO_INICIAL)

        for i in range(SCROLLS):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(10,20))

        tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        logging.info(f"✍️ {len(tweets)} tweets encontrados para {empresa}")

        for tweet in tweets:
            try:
                texto = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
                autor = tweet.find_element(By.XPATH, './/div[@dir="ltr"]/span').text
                link = tweet.find_element(By.XPATH, './/a[@role="link"]').get_attribute("href")

                if any(palabra in texto.lower() for palabra in KEYWORDS):
                    tweets_finales.append({
                        "empresa": empresa,
                        "usuario": autor,
                        "contenido": texto,
                        "url": f"https://twitter.com{link}" if not link.startswith("http") else link,
                        "fecha_scrapeo": datetime.now().isoformat()
                    })

            except NoSuchElementException:
                continue

    except Exception as e:
        logging.warning(f"⚠️ Fallo scrapeo para {empresa}: {e}")

    #driver.quit()

    nombre_archivo = f"tweets_merval_selenium_{datetime.today().date()}.json"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(tweets_finales, f, indent=2, ensure_ascii=False)

    logging.info(f"✅ Se guardaron {len(tweets_finales)} tweets en {nombre_archivo}")

if __name__ == "__main__":
    scrapear_tweets()
