import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import random
from datetime import datetime
import re
import os  # Necessario per gestire le cartelle

def pulisci_nome_file(testo):
    """Rimuove caratteri non validi per i nomi dei file"""
    return re.sub(r'[\\/*?:"<>|.]', '', testo).replace(" ", "_")

def cerca_linkedin_automation(azienda, regione=""):
    print(f"\n[SISTEMA] Avvio browser Chrome...")
    options = uc.ChromeOptions()
    
    driver = uc.Chrome(options=options)
    
    try:
        azienda_clean = azienda.replace(".", "").strip()
        query = f'site:linkedin.com/in/ "{azienda_clean}"'
        if regione:
            query += f' "{regione}"'
            
        print(f"[INFO] Ricerca in corso per: {query}")
        
        driver.get(f"https://www.google.com/search?q={query}")
        
        print("[INFO] Aspetto 5 secondi per il caricamento...")
        time.sleep(5) 
        
        # Gestione Cookie
        try:
            for btn in driver.find_elements(By.TAG_NAME, "button"):
                if any(x in btn.text for x in ["Accetta", "Acepto", "Agree"]):
                    btn.click()
                    time.sleep(2)
                    break
        except: 
            pass

        profili = []
        
        # Estrazione link LinkedIn
        tutti_i_link = driver.find_elements(By.XPATH, "//a[contains(@href, 'linkedin.com/in/')]")
        
        for elem in tutti_i_link:
            try:
                url = elem.get_attribute("href")
                titolo = elem.text
                
                if not titolo:
                    try:
                        titolo = elem.find_element(By.XPATH, ".//h3").text
                    except:
                        continue

                if url and "google.com" not in url and url not in [p['Link'] for p in profili]:
                    parti = titolo.split(" - ")
                    nome = parti[0].replace("LinkedIn", "").strip() if len(parti) > 0 else "N/D"
                    ruolo = parti[1].strip() if len(parti) > 1 else "N/D"

                    print(f"[OK] Trovato: {nome}")
                    profili.append({
                        "Nome": nome,
                        "Ruolo": ruolo,
                        "Azienda": azienda,
                        "Regione": regione if regione else "N/D",
                        "Link": url
                    })
            except:
                continue
                
        print(f"[INFO] Trovati {len(profili)} profili.")
        return profili

    except Exception as e:
        print(f"[ERRORE] {e}")
        return []
    finally:
        print("[SISTEMA] Chiusura browser.")
        driver.quit()

if __name__ == "__main__":
    print("=== LINKEDIN DORKER V7 (EXPORTS FOLDER) ===")
    az_input = input("Azienda: ")
    reg_input = input("Regione: ")
    
    dati = cerca_linkedin_automation(az_input, reg_input)
    
    if dati:
        # 1. Crea la cartella 'exports' se non esiste
        folder = "exports"
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"[SISTEMA] Cartella '{folder}' creata.")

        # 2. Prepara il nome del file
        df = pd.DataFrame(dati)
        nome_azienda_safe = pulisci_nome_file(az_input)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_file = f"estrazione_{nome_azienda_safe}_{timestamp}.xlsx"
        
        # 3. Costruisce il percorso completo (exports/nome_file.xlsx)
        percorso_completo = os.path.join(folder, nome_file)
        
        df.to_excel(percorso_completo, index=False)
        print(f"\n✅ SUCCESSO! File salvato in: {percorso_completo}")
    else:
        print("\n[!] Nessun risultato trovato.")