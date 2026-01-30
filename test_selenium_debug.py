"""Test détaillé du scraper Selenium avec débogage complet"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

test_url = "https://www.scan-manga.com/lecture-en-ligne/Eleceed-Chapitre-363-FR_498341.html"

print("=" * 80)
print("TEST SELENIUM AVEC DÉBOGAGE COMPLET")
print("=" * 80)
print(f"\nURL: {test_url}\n")

# Configuration Chrome
chrome_options = Options()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')

# Mode headless commenté pour voir ce qui se passe
# chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

print("🔧 Création du driver Chrome...")
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print("✅ Driver créé avec succès\n")
except Exception as e:
    print(f"❌ Erreur lors de la création du driver: {e}")
    exit(1)

try:
    print(f"🌐 Chargement de la page...")
    driver.get(test_url)
    
    print(f"⏳ Attente du chargement...")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    
    print(f"⏳ Attente supplémentaire pour le lazy loading (3 secondes)...")
    time.sleep(3)
    
    print(f"✅ Page chargée\n")
    print(f"📄 Titre de la page: {driver.title}\n")
    
    # Récupérer le HTML
    html = driver.page_source
    
    # Sauvegarder
    output_file = "selenium_debug.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"💾 HTML sauvegardé dans: {output_file}\n")
    
    # Parser avec BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Analyser les images
    print("=" * 80)
    print("ANALYSE DES IMAGES")
    print("=" * 80)
    
    # Meta tags
    print("\n1. META TAGS:")
    meta_og = soup.find("meta", {"property": "og:image"})
    if meta_og:
        print(f"   ✅ og:image = {meta_og.get('content')}")
    else:
        print("   ❌ Pas de og:image")
    
    meta_twitter = soup.find("meta", {"name": "twitter:image"})
    if meta_twitter:
        print(f"   ✅ twitter:image = {meta_twitter.get('content')}")
    else:
        print("   ❌ Pas de twitter:image")
    
    # Toutes les images
    print("\n2. IMAGES TROUVÉES:")
    all_imgs = soup.find_all('img')
    print(f"   Total: {len(all_imgs)} images\n")
    
    for i, img in enumerate(all_imgs[:15], 1):
        print(f"   Image #{i}:")
        src = img.get('src', 'N/A')
        data_src = img.get('data-src', 'N/A')
        alt = img.get('alt', 'N/A')
        classes = img.get('class', [])
        
        print(f"      src: {src[:100] if src != 'N/A' else 'N/A'}")
        if data_src != 'N/A':
            print(f"      data-src: {data_src[:100]}")
        print(f"      alt: {alt[:50] if alt != 'N/A' else 'N/A'}")
        print(f"      class: {classes}")
        print()
    
    # Chercher des patterns spécifiques
    print("\n3. SÉLECTEURS SPÉCIFIQUES:")
    selectors = [
        ".manga-cover img",
        ".post-thumbnail img",
        ".entry-thumb img",
        ".wp-post-image",
        "img[class*='cover']",
        "img[class*='poster']",
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            print(f"   ✅ '{selector}': {len(elements)} trouvé(s)")
            for elem in elements[:2]:
                print(f"      → {elem.get('src', elem.get('data-src', 'N/A'))[:80]}")
        else:
            print(f"   ❌ '{selector}': aucun")
    
    print("\n" + "=" * 80)
    print("✅ Analyse terminée - Vérifiez le fichier selenium_debug.html")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n🔒 Fermeture du driver...")
    driver.quit()
    print("✅ Terminé")
