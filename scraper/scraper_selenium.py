"""
Scraper utilisant Selenium pour contourner les protections anti-bot
Nécessite: pip install selenium webdriver-manager
"""
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from .scraper import (
    _extract_title_from_url,
    _extract_chapter_from_url,
    _is_valid_manga_image,
    _score_manga_image,
    _clean_text,
    PLACEHOLDER_IMG
)

def create_selenium_driver():
    """Crée un driver Selenium avec options anti-détection"""
    if not SELENIUM_AVAILABLE:
        raise ImportError("Selenium n'est pas installé. Exécutez: pip install selenium webdriver-manager")
    
    chrome_options = Options()
    
    # Options pour éviter la détection
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent réaliste
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    
    # Mode headless (optionnel - commentez pour voir le navigateur)
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # Créer le driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Modifier le navigator.webdriver flag
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def scrape_manga_info_selenium(url: str) -> dict:
    """Scrape les informations du manga avec Selenium"""
    
    print(f"[SELENIUM] Démarrage du scraping pour: {url}")
    
    driver = None
    try:
        driver = create_selenium_driver()
        
        print(f"[SELENIUM] Chargement de la page...")
        driver.get(url)
        
        # Attendre que la page soit chargée
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Attendre un peu pour le lazy loading des images
        import time
        time.sleep(2)
        
        print(f"[SELENIUM] Page chargée avec succès")
        
        # Récupérer le HTML
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Sauvegarder pour debug
        with open('selenium_debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[SELENIUM] HTML sauvegardé dans selenium_debug.html")
        
        # Extraire les informations
        title = None
        img = None
        resume = None
        
        # 1. TITRE
        title = _extract_title_from_url(url)
        if not title:
            title_selectors = [
                "h1.entry-title",
                "h1.post-title",
                "h1",
            ]
            for selector in title_selectors:
                try:
                    element = soup.select_one(selector)
                    if element:
                        candidate = _clean_text(element.get_text())
                        if candidate and len(candidate) > 3:
                            cleaned_title = re.sub(r'\s*-?\s*Chapitre\s*\d+.*$', '', candidate, flags=re.IGNORECASE)
                            title = _clean_text(cleaned_title)
                            if title:
                                print(f"[SELENIUM] Titre trouvé: {title}")
                                break
                except:
                    continue
        
        # 2. IMAGE
        print(f"[SELENIUM] Recherche de l'image...")
        
        # Meta tags
        meta_og = soup.find("meta", {"property": "og:image"})
        if meta_og:
            candidate = meta_og.get("content")
            if candidate and _is_valid_manga_image(candidate):
                img = candidate if candidate.startswith('http') else urljoin(url, candidate)
                print(f"[SELENIUM] Image trouvée via og:image: {img}")
        
        # Recherche dans toutes les images
        if not img:
            all_imgs = soup.find_all('img')
            print(f"[SELENIUM] {len(all_imgs)} images trouvées")
            
            valid_images = []
            for img_tag in all_imgs:
                for attr in ['src', 'data-src', 'data-lazy-src', 'data-original', 'srcset']:
                    candidate = img_tag.get(attr)
                    if candidate:
                        # Gérer srcset
                        if attr == 'srcset' and ',' in candidate:
                            candidate = candidate.split(',')[0].strip().split(' ')[0]
                        
                        # Construire URL complète
                        if candidate.startswith('//'):
                            full_url = 'https:' + candidate
                        elif candidate.startswith('/'):
                            full_url = urljoin(url, candidate)
                        elif not candidate.startswith('http'):
                            full_url = urljoin(url, candidate)
                        else:
                            full_url = candidate
                        
                        if _is_valid_manga_image(full_url):
                            score = _score_manga_image(full_url, img_tag)
                            valid_images.append((score, full_url))
                            print(f"[SELENIUM] Image valide (score: {score}): {full_url[:80]}...")
            
            if valid_images:
                valid_images.sort(reverse=True, key=lambda x: x[0])
                img = valid_images[0][1]
                print(f"[SELENIUM] ✅ Meilleure image sélectionnée: {img}")
        
        # 3. RÉSUMÉ
        resume_selectors = [
            ".manga-summary",
            ".manga-description",
            ".synopsis",
            ".entry-content p",
        ]
        
        for selector in resume_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    candidate = _clean_text(element.get_text())
                    if candidate and len(candidate) > 30:
                        resume = candidate[:500]
                        break
            except:
                continue
        
        # Fallbacks
        if not title:
            title = "Manga Inconnu"
        
        if not img:
            img = PLACEHOLDER_IMG
            print(f"[SELENIUM] ⚠️  Aucune image trouvée, utilisation du placeholder")
        
        chapitre = _extract_chapter_from_url(url)
        
        result = {
            "titre": title,
            "chapitre": chapitre,
            "image": img,
            "resume": resume,
            "source": "scan-manga",
        }
        
        print(f"[SELENIUM] Résultat: {result}")
        return result
        
    except Exception as e:
        print(f"[SELENIUM ERROR] {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback
        return {
            "titre": _extract_title_from_url(url) or "Manga Inconnu",
            "chapitre": _extract_chapter_from_url(url),
            "image": PLACEHOLDER_IMG,
            "resume": None,
            "source": "scan-manga",
        }
    
    finally:
        if driver:
            driver.quit()
            print(f"[SELENIUM] Driver fermé")

if __name__ == "__main__":
    # Test
    test_url = "https://www.scan-manga.com/lecture-en-ligne/Eleceed-Chapitre-363-FR_498341.html"
    result = scrape_manga_info_selenium(test_url)
    
    print("\n" + "=" * 80)
    print("RÉSULTAT FINAL:")
    print("=" * 80)
    for key, value in result.items():
        if key == 'resume' and value:
            print(f"{key}: {value[:100]}...")
        else:
            print(f"{key}: {value}")
