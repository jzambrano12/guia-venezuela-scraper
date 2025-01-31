import csv
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Configuración de Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Ejecución sin interfaz gráfica
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

# Reutilizamos las mismas profesiones y URLs
professions = [
    # Abogados
    "abogados+penalistas", "abogados+laborales", "abogados+civiles", "abogados+comerciales", 
    "abogados+tributarios", "abogados+de+familia", "abogados+inmobiliarios", "abogados+de+seguros",
    
    # Médicos
    "medicos+generales", "medicos+pediatras", "medicos+cardiologos", "medicos+dermatologos",
    "medicos+ginecologos", "medicos+oftalmologos", "medicos+ortopedistas", "medicos+psiquiatras",
    
    # Ingenieros
    "ingenieros+civiles+estructurales", "ingenieros+civiles+hidraulicos", "ingenieros+electricos+industriales",
    "ingenieros+mecanicos+automotrices", "ingenieros+de+sistemas", "ingenieros+de+telecomunicaciones",
    "ingenieros+quimicos", "ingenieros+ambientales",
    
    # Arquitectos
    "arquitectos+de+interiores", "arquitectos+paisajistas", "arquitectos+urbanistas",
    
    # Contadores
    "contadores+auditores", "contadores+tributarios", "contadores+financieros",
    
    # Dentistas
    "dentistas+ortodoncistas", "dentistas+implantologos", "dentistas+esteticos",
    
    # Psicólogos
    "psicologos+clinicos", "psicologos+organizacionales", "psicologos+infantiles",
    
    # Veterinarios
    "veterinarios+de+pequenos+animales", "veterinarios+de+grandes+animales", "veterinarios+exoticos",
    
    # Técnicos
    "tecnicos+en+refrigeracion+industrial", "tecnicos+en+aire+acondicionado+automotriz",
    "tecnicos+en+electronica+medica", "tecnicos+en+informatica+de+redes",
    "tecnicos+en+energias+renovables+solar", "tecnicos+en+energias+renovables+eolica",
    
    # Diseño y Programación
    "disenadores+graficos+web", "disenadores+graficos+3d", "programadores+web",
    "programadores+mobile", "programadores+de+inteligencia+artificial",
    
    # Otros profesionales
    "consultores+de+negocios+internacionales", "asesores+financieros+personales",
    "fotografos+de+bodas", "fotografos+de+productos", "chefs+pasteleros",
    "nutricionistas+deportivos", "entrenadores+personales+de+crossfit",
    "masajistas+terapeuticos", "estilistas+de+cejas", "barberos+esteticos",
    "tecnicos+en+sonido+en+vivo", "tecnicos+en+seguridad+electronica",
    "jardineros+de+paisajismo", "traductores+jurados", "organizadores+de+eventos+corporativos",
    "instructores+de+yoga+prenatal", "asesores+inmobiliarios+comerciales"
    "electricistas", "plomeros", "carpinteros", "albañiles", "mecanicos"
]

base_url = "https://guiavenezuela.com.ve/buscar.php?c={profession}&localidad_busca=Maracaibo%2C+Zulia&idLocalidad_busca=366&submit="
urls_to_scrape = [base_url.format(profession=profession) for profession in professions]

def extract_phone_number(driver, phone_id):
    try:
        # Limpiar cualquier iframe existente antes de empezar
        driver.execute_script("if(typeof $.fancybox !== 'undefined') { $.fancybox.close(); }")
        time.sleep(1)
        
        # Encontrar el botón específico por ID
        phone_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, phone_id))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", phone_button)
        time.sleep(1)
        
        # Hacer clic usando JavaScript
        driver.execute_script("arguments[0].click();", phone_button)
        time.sleep(1)
        
        # Esperar a que el iframe esté presente
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "fancybox-iframe"))
        )
        
        # Cambiar al iframe
        driver.switch_to.frame(iframe)
        time.sleep(1)
        
        # Obtener los números
        phone_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "telNro"))
        )
        phone_numbers = " / ".join([elem.text.strip() for elem in phone_elements])
        
        # Volver al contexto principal
        driver.switch_to.default_content()
        
        # Cerrar el popup
        try:
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "fancybox-close"))
            )
            close_button.click()
        except:
            driver.execute_script("if(typeof $.fancybox !== 'undefined') { $.fancybox.close(); }")
        
        time.sleep(2)
        return phone_numbers if phone_numbers else "NaN"
        
    except Exception as e:
        print(f"Error extracting phone number for ID {phone_id}: {str(e)}")
        return "NaN"
    finally:
        try:
            driver.switch_to.default_content()
            driver.execute_script("if(typeof $.fancybox !== 'undefined') { $.fancybox.close(); }")
            # Forzar recarga del DOM
            driver.execute_script("document.body.style.display='none'; document.body.offsetHeight; document.body.style.display='';")
            time.sleep(1)
        except:
            pass

def extract_professionals_data(driver, url):
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.e'))
            )
            time.sleep(1)
            break
        except Exception as e:
            print(f"Error loading URL (attempt {retry_count + 1}/{max_retries}): {str(e)}")
            retry_count += 1
            if retry_count == max_retries:
                print("Failed to load URL after maximum retries")
                return []
            # Reset driver if session is invalid
            if "invalid session id" in str(e).lower():
                print("Resetting driver due to invalid session...")
                driver.quit()
                driver = webdriver.Chrome(options=options)
            time.sleep(5)
    
    professionals = []
    
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Encontrar todos los contenedores de profesionales
        for card in soup.select('div.e'):
            try:
                # Extraer nombre
                name_element = card.select_one('div.ee strong a') or card.select_one('div.eSe strong')
                name = name_element.text.strip() if name_element else "NaN"
                print(f"\nProcessing professional: {name}")
                
                # Extraer dirección
                address = card.select_one('p.d').text.strip() if card.select_one('p.d') else "NaN"
                
                # Extraer teléfono
                phone = "NaN"
                phone_button = card.select_one('img.bg.verTelefono')
                if phone_button:
                    phone_id = phone_button.get('id', '')
                    if phone_id:
                        try:
                            print(f"Attempting to get phone for ID: {phone_id}")
                            phone = extract_phone_number(driver, phone_id)
                            print(f"Phone number extracted: {phone}")
                            
                            # Refrescar el DOM después de cada extracción
                            driver.execute_script("document.body.style.display='none'; document.body.offsetHeight; document.body.style.display='';")
                            time.sleep(3)
                            
                        except Exception as e:
                            print(f"Error getting phone for {name}: {str(e)}")
                            phone = "NaN"
                            if "Connection refused" in str(e):
                                print("Connection lost, refreshing page...")
                                driver.refresh()
                                time.sleep(5)
                
                # Extraer descripción
                description = card.select_one('div.ee p:not(.d)').text.strip() if card.select_one('div.ee p:not(.d)') else "NaN"
                
                professionals.append({
                    "name": name,
                    "address": address,
                    "phone": phone,
                    "description": description
                })
                
            except Exception as card_error:
                print(f"Error processing card: {str(card_error)}")
                continue
            
    except Exception as e:
        print(f"Error processing page: {str(e)}")
    
    return professionals

def main():
    driver = webdriver.Chrome(options=options)
    output_csv_path = "results.csv"
    last_url_time = time.time()  # Añadir tracking de tiempo
    
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csv_file:
        csv_columns = ["url", "profession", "name", "address", "phone", "description"]
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()
        
        successful = 0
        total_professionals = 0
        
        for idx, url in enumerate(urls_to_scrape, 1):
            current_time = time.time()
            minutes_elapsed = (current_time - last_url_time) / 60
            print(f"\nProcessing URL {idx}/{len(urls_to_scrape)}: {url}")
            print(f"Time since last URL: {minutes_elapsed:.2f} minutes")
            last_url_time = current_time  # Actualizar el tiempo para la siguiente iteración
            
            try:
                profession = url.split("c=")[1].split("&")[0].replace("+", " ")
                professionals = extract_professionals_data(driver, url)
                
                for pro in professionals:
                    writer.writerow({
                        "url": url,
                        "profession": profession,
                        "name": pro["name"],
                        "address": pro["address"],
                        "phone": pro["phone"],
                        "description": pro["description"],
                    })
                    total_professionals += 1
                
                print(f"✓ {len(professionals)} professionals found")
                successful += 1
                
            except Exception as e:
                print(f"✗ Error processing URL: {str(e)}")
                # Handle session expiration during processing
                if "invalid session id" in str(e).lower():
                    print("Reinitializing driver...")
                    driver.quit()
                    driver = webdriver.Chrome(options=options)
                    time.sleep(2)
                    # Retry current URL
                    idx -= 1
                    continue
            
            csv_file.flush()
            time.sleep(1)  # Delay entre requests
    
    driver.quit()
    print(f"\nScraping completed. Results saved to {output_csv_path}")
    print(f"Successfully processed: {successful}/{len(urls_to_scrape)}")
    print(f"Total professionals collected: {total_professionals}")

if __name__ == "__main__":
    main() 




    