import json
import os
import subprocess
import logging
from scraper_twitter import scrapear_tweets
from scraper_iprofesional import scrapear_iprofesional
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager

#empresa = "$YPF"

# === Cargar equivalencias de empresas del MERVAL ===
with open("empresas_merval_equivalencias.json", "r", encoding="utf-8") as f:
    equivalencias = json.load(f)

def detectar_empresas(equivalencias):
    #texto = texto.lower()
    empresas = []
    for empresa in equivalencias.items():
        for alias in empresa:
            empresas.append(alias)  # Agrega el nombre de la empresa
    return empresas

empresas_detectadas = [sinonimos[1] for sinonimos in equivalencias.values() if len(sinonimos) > 1]


# Función para matar procesos previos
def matar_edge():
    logging.info("🧨 Cerrando Edge y msedgedriver previos…")
    subprocess.call("taskkill /f /im msedge.exe", shell=True, stderr=subprocess.DEVNULL)
    subprocess.call("taskkill /f /im msedgedriver.exe", shell=True, stderr=subprocess.DEVNULL)

def configurar_driver_local():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--user-data-dir=C:/Users/Luciano/AppData/Local/Microsoft/Edge/User Data")
    options.add_argument("--profile-directory=Profile 1")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Ruta local al driver de Edge (ajustá el path si es necesario)
    path_driver = "C:\\Users\\Luciano\\Desktop\\UADE\\PFI\\programa\\pfi_mervAI\\drivers\\msedgedriver.exe"

    service = Service(path_driver)
    driver = webdriver.Edge(service=service, options=options)
    return driver

def main_scrapper():
    matar_edge()
    print("Iniciando scrapper principal...")
    driver = configurar_driver_local()
    try:
        for emp in empresas_detectadas:
            print(f"Detectada empresa: {emp}")
            scrapear_tweets(emp, driver)
        scrapear_iprofesional(driver, equivalencias)
    finally:
        driver.quit()


if __name__ == "__main__":
    main_scrapper()