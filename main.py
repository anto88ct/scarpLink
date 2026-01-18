import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os
import random
import traceback # Per i log dettagliati
from datetime import datetime

CHROME_PROFILE_PATH = os.path.abspath("chrome_data")

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions") 
    driver = uc.Chrome(options=options)
    return driver

def cerca_e_estrai_tutti(driver, azienda):
    pagina = 1
    tutti_i_risultati = []
    
    while True:
        try:
            print(f"\n[SISTEMA] 📄 Analisi Pagina {pagina}...")
            url = f"https://www.linkedin.com/search/results/people/?keywords={azienda}&origin=GLOBAL_SEARCH_CARD&page={pagina}"
            driver.get(url)
            
            # Aspetta il caricamento iniziale (LinkedIn è pesante)
            time.sleep(random.uniform(6, 9))

            # Rimuove banner
            try: driver.execute_script("document.querySelector('section.dba91374')?.remove();")
            except: pass

            # SCROLL LENTO (Fondamentale per i contenuti dinamici)
            for s in range(1, 11):
                driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {s/10});")
                time.sleep(0.4)
            
            # ATTESA POTENZIATA (30 secondi)
            try:
                wait = WebDriverWait(driver, 30)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="listitem"]')))
            except Exception as e:
                print(f"[!] Timeout alla pagina {pagina}. Provo un refresh...")
                driver.refresh()
                time.sleep(10)
                # Se dopo il refresh non c'è ancora nulla, allora i risultati sono finiti
                if not driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]'):
                    print("[SISTEMA] Risultati terminati o blocco temporaneo.")
                    break

            items = driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')
            
            for item in items:
                try:
                    link_elem = item.find_element(By.CSS_SELECTOR, 'a[data-view-name="search-result-lockup-title"]')
                    nome_completo = link_elem.text.split("\n")[0].strip()
                    nome = nome_completo.split(" • ")[0].strip()
                    url_profilo = link_elem.get_attribute("href").split("?")[0]
                    
                    descrizioni = item.find_elements(By.TAG_NAME, "p")
                    ruolo = descrizioni[1].text.strip() if len(descrizioni) >= 2 else "N/D"
                    localita = descrizioni[2].text.strip() if len(descrizioni) >= 3 else "N/D"

                    if nome and "Membro di LinkedIn" not in nome:
                        if url_profilo not in [r['LINK'] for r in tutti_i_risultati]:
                            print(f"[OK] {nome} | {ruolo[:40]}...")
                            tutti_i_risultati.append({
                                "NOME": nome, "RUOLO": ruolo, "LOCALITÀ": localita, "LINK": url_profilo
                            })
                except: continue

            # PAGINAZIONE
            next_button = driver.find_elements(By.CSS_SELECTOR, 'button[data-testid="pagination-controls-next-button-visible"]')
            if next_button and "hidden" not in next_button[0].get_attribute("data-testid"):
                pagina += 1
                time.sleep(random.uniform(5, 10)) # Più tempo tra le pagine per evitare timeout
            else:
                break

        except Exception:
            # SALVATAGGIO LOG ERRORE
            with open("debug_log.txt", "w") as f:
                f.write(traceback.format_exc())
            print(f"[!] ERRORE CRITICO alla pagina {pagina}. Log salvato in 'debug_log.txt'.")
            break
            
    return tutti_i_risultati

if __name__ == "__main__":
    if not os.path.exists(CHROME_PROFILE_PATH): os.makedirs(CHROME_PROFILE_PATH)
    az_input = input("Azienda: ")
    driver = setup_driver()

    try:
        driver.get("https://www.linkedin.com/feed/")
        while not driver.find_elements(By.ID, "global-nav"): time.sleep(5)
        print("[SUCCESSO] Login rilevato!")

        dati = cerca_e_estrai_tutti(driver, az_input)

        if dati:
            if not os.path.exists("exports"): os.makedirs("exports")
            df = pd.DataFrame(dati)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"exports/FULL_ESTRAZIONE_{az_input}_{ts}.xlsx"
            df.to_excel(path, index=False)
            print(f"\n✅ FINITO! {len(dati)} profili salvati.")
    finally:
        driver.quit()