import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os
import random
import subprocess
import traceback
from datetime import datetime
import re

# --- CONFIGURAZIONE PERCORSI ---
CHROME_PROFILE_PATH = os.path.abspath("chrome_data")
EXPORT_FOLDER = os.path.abspath("exports")

st.set_page_config(page_title="LinkedIn Deep Finder", page_icon="🕵️‍♂️", layout="wide")

# --- FUNZIONI DI SUPPORTO ---
def pulisci_nome_file(testo):
    return re.sub(r'[\\/*?:"<>|.]', '', testo).replace(" ", "_")

def apri_cartella_exports():
    if not os.path.exists(EXPORT_FOLDER):
        os.makedirs(EXPORT_FOLDER)
    if os.name == 'nt': # Windows
        os.startfile(EXPORT_FOLDER)
    else: # Mac/Linux
        subprocess.call(['open' if os.name == 'posix' else 'xdg-open', EXPORT_FOLDER])

def scraping_logic(azienda):
    """Logica V14/V15 calibrata sull'HTML reale"""
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    
    driver = uc.Chrome(options=options)
    tutti_i_risultati = []
    
    try:
        # 1. Controllo Sessione
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(4)
        
        if not driver.find_elements(By.ID, "global-nav"):
            st.info("👋 Effettua il login nella finestra di Chrome per iniziare...")
            while not driver.find_elements(By.ID, "global-nav"):
                time.sleep(3)
            st.toast("Accesso rilevato!", icon="✅")

        # 2. Ciclo di Estrazione Pagine
        pagina = 1
        while True:
            url = f"https://www.linkedin.com/search/results/people/?keywords={azienda}&origin=GLOBAL_SEARCH_CARD&page={pagina}"
            driver.get(url)
            time.sleep(random.uniform(6, 8))

            # Rimuove banner fastidiosi
            try: driver.execute_script("document.querySelector('section.dba91374')?.remove();")
            except: pass

            # Scroll lento per caricare tutto (10 step)
            for s in range(1, 11):
                driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {s/10});")
                time.sleep(0.3)

            try:
                # Aspetta i risultati (div role listitem)
                wait = WebDriverWait(driver, 25)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="listitem"]')))
                
                items = driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')
                
                for item in items:
                    try:
                        # Estrazione Nome e Link (da data-view-name)
                        link_elem = item.find_element(By.CSS_SELECTOR, 'a[data-view-name="search-result-lockup-title"]')
                        nome_raw = link_elem.text.split("\n")[0].strip()
                        nome = nome_raw.split(" • ")[0].strip()
                        url_p = link_elem.get_attribute("href").split("?")[0]
                        
                        # Estrazione Posizionale dei paragrafi (Sotto-titoli)
                        # p[0] Nome, p[1] Ruolo, p[2] Località
                        paragrafi = item.find_elements(By.TAG_NAME, "p")
                        ruolo = paragrafi[1].text.strip() if len(paragrafi) >= 2 else "N/D"
                        localita = paragrafi[2].text.strip() if len(paragrafi) >= 3 else "N/D"

                        if nome and "Membro di LinkedIn" not in nome:
                            if url_p not in [r['LINK'] for r in tutti_i_risultati]:
                                tutti_i_risultati.append({
                                    "NOME": nome, 
                                    "RUOLO": ruolo, 
                                    "LOCALITÀ": localita, 
                                    "LINK": url_p
                                })
                    except: continue

                # Paginazione (Usa data-testid visto nell'HTML)
                next_btn = driver.find_elements(By.CSS_SELECTOR, 'button[data-testid="pagination-controls-next-button-visible"]')
                if next_btn and "hidden" not in next_btn[0].get_attribute("data-testid"):
                    pagina += 1
                    time.sleep(random.uniform(4, 7))
                else:
                    break # Fine risultati
            except Exception:
                # In caso di timeout, proviamo a vedere se abbiamo almeno dei risultati
                if len(tutti_i_risultati) > 0: break
                else: raise # Se non abbiamo nulla, solleva errore

        return tutti_i_risultati

    except Exception:
        with open("debug_log_ui.txt", "w") as f:
            f.write(traceback.format_exc())
        return "ERROR"
    finally:
        driver.quit()

# --- INTERFACCIA STREAMLIT ---
st.title("🕵️‍♂️ LinkedIn Deep Finder Pro")

# 1. Spiegazione Tool
with st.expander("❓ Come funziona questo strumento?", expanded=False):
    st.markdown("""
    Questo tool esegue una scansione profonda dei dipendenti di un'azienda su LinkedIn bypassando i limiti del Dorking classico.
    
    * **Estrazione Intelligente**: Non si basa sui nomi delle classi (che cambiano sempre), ma sulla struttura del documento (paragrafi posizionali).
    * **Dati estratti**: Nome, Ruolo (sottotitolo), Località e Link al profilo.
    * **Paginazione Automatica**: Naviga tra le pagine dei risultati finché non finiscono i dipendenti.
    * **Sessione Persistente**: Chrome ricorderà il tuo login grazie alla cartella `chrome_data`.
    """)

# 2. Sidebar con Ricerca e Cartella
st.sidebar.header("🔍 Ricerca")
azienda_target = st.sidebar.text_input("Azienda da scansionare", placeholder="Es: Seedma srl")

st.sidebar.divider()
col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    avvia = st.button("🚀 Avvia", use_container_width=True)
with col_btn2:
    apri_folder = st.button("📂 Exports", use_container_width=True)

if apri_folder:
    apri_cartella_exports()

# 3. Area Risultati
if avvia:
    if not azienda_target:
        st.warning("⚠️ Inserisci il nome dell'azienda.")
    else:
        progress_bar = st.progress(0)
        with st.spinner(f"Analisi profonda di '{azienda_target}' in corso..."):
            risultati = scraping_logic(azienda_target)
            progress_bar.progress(100)
            
            if risultati == "ERROR":
                st.error("❌ Si è verificato un errore tecnico. Controlla 'debug_log_ui.txt'.")
            elif risultati:
                df = pd.DataFrame(risultati)
                st.success(f"✅ Scansione completata! Trovati {len(df)} profili.")
                
                # Anteprima Tabella
                st.dataframe(df, use_container_width=True)
                
                # Salvataggio File
                if not os.path.exists(EXPORT_FOLDER): os.makedirs(EXPORT_FOLDER)
                nome_f = f"DEEP_SCAN_{pulisci_nome_file(azienda_target)}_{datetime.now().strftime('%H%M%S')}.xlsx"
                percorso = os.path.join(EXPORT_FOLDER, nome_f)
                df.to_excel(percorso, index=False)
                
                # Download button
                with open(percorso, "rb") as f:
                    st.download_button("📥 Scarica Report Excel", f, file_name=nome_f)
            else:
                st.error("❌ Nessun profilo trovato o errore nel caricamento della pagina.")

st.divider()
st.caption(f"Status: Pronto | Cartella Sessione: `{CHROME_PROFILE_PATH}`")