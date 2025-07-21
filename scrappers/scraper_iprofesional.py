import json
import time
import random
import logging
from datetime import datetime, timedelta
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

def detectar_empresas(texto, equivalencias):
    texto = texto.lower()
    empresas = []
    for empresa, sinonimos in equivalencias.items():
        for s in sinonimos:
            if s.lower() in texto:
                empresas.append(empresa)
                break
    return empresas

def scrapear_iprofesional(driver,equivalencias):
    #driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)

    driver.get(URL_BASE)
    logging.info("🔍 Cargando iProfesional Finanzas…")
    time.sleep(TIME_SLEEP)

    for i in range(SCROLLS):
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(random.uniform(3, 5))

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
                fecha_raw = driver.find_element(By.CSS_SELECTOR, ".date").text
                fecha_publicacion = datetime.strptime(fecha_raw.split("|")[0].strip(), "%d/%m/%Y")
            except:
                fecha_publicacion = datetime.now()

            # Filtrar por últimas 24hs
            if fecha_publicacion < datetime.now() - timedelta(days=1):
                continue

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

            texto_para_match = f"{titulo} {resumen} {texto_completo}"
            empresas_relacionadas = detectar_empresas(texto_para_match, equivalencias)

            noticias.append({
                "fecha_scrapeo": datetime.now().isoformat(),
                "titulo": titulo,
                "autor": autor,
                "fecha_publicacion": fecha_publicacion.isoformat(),
                "resumen": resumen,
                "contenido_completo": texto_completo,
                "url": url,
                "empresas_merval": empresas_relacionadas
            })

            logging.info(f"📝 {titulo[:60]}...")

        except Exception as e:
            logging.warning(f"❌ Error en {url}: {e}")
            with open("debug_iprofesional.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)

    #driver.quit()

    archivo = f"iprofesional_finanzas_{datetime.today().date()}.json"
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(noticias, f, indent=2, ensure_ascii=False)
    logging.info(f"💾 {len(noticias)} noticias guardadas en {archivo}")

if __name__ == "__main__":
    scrapear_iprofesional()
