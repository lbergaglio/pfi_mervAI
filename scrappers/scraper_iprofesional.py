import json
import time
import random
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# === Configuración ===
URL_BASE = "https://www.iprofesional.com/finanzas"
TIME_SLEEP = 5
SCROLLS = 2

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def scrapear_iprofesional():
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)

    driver.get(URL_BASE)
    logging.info("🔍 Cargando iProfesional Finanzas…")
    time.sleep(TIME_SLEEP)

    # Scroll para cargar más artículos
    for i in range(SCROLLS):
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(random.uniform(3, 5))

    # Obtener enlaces de noticias
    articulos = driver.find_elements(By.CSS_SELECTOR, "a[href*='/finanzas/']")
    urls = []
    for a in articulos:
        href = a.get_attribute("href")
        if href and href not in urls:
            urls.append(href)
    logging.info(f"🔗 {len(urls)} links encontrados.")

    noticias = []
    for url in urls:
        try:
            driver.get(url)
            time.sleep(random.uniform(4, 6))

            titulo = driver.find_element(By.TAG_NAME, "h1").text

            try:
                autor = driver.find_element(By.CSS_SELECTOR, ".single-author").text
            except:
                autor = "[No especificado]"

            try:
                fecha = driver.find_element(By.CSS_SELECTOR, ".date").text
            except:
                fecha = datetime.now().isoformat()

            # === NUEVO BLOQUE ROBUSTO PARA PÁRRAFOS ===
            posibles_contenedores = [
                "article", ".note-body", ".article-body", ".container-body", ".article-container", ".story-content"
            ]

            parrafos = []
            for selector in posibles_contenedores:
                try:
                    contenedor = driver.find_element(By.CSS_SELECTOR, selector)
                    parrafos = contenedor.find_elements(By.TAG_NAME, "p")
                    if len(parrafos) > 3:
                        break
                except:
                    continue

            texto_completo = " ".join(p.text for p in parrafos if p.text.strip())
            resumen = " ".join(p.text for p in parrafos[:5])

            noticias.append({
                "fecha_scrapeo": datetime.now().isoformat(),
                "titulo": titulo,
                "autor": autor,
                "fecha_publicacion": fecha,
                "resumen": resumen,
                "contenido_completo": texto_completo,
                "url": url
            })

            logging.info(f"📝 {titulo[:60]}...")

        except Exception as e:
            logging.warning(f"❌ Error en {url}: {e}")
            with open("debug_iprofesional.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)

    driver.quit()

    archivo = f"iprofesional_finanzas_{datetime.today().date()}.json"
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(noticias, f, indent=2, ensure_ascii=False)
    logging.info(f"💾 {len(noticias)} noticias guardadas en {archivo}")

if __name__ == "__main__":
    scrapear_iprofesional()
