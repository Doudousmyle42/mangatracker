"""Script de débogage avancé pour le scraper"""
import requests
from bs4 import BeautifulSoup
from scraper.scraper import create_session
import sys

# URL de test - remplacez par votre URL
if len(sys.argv) > 1:
    test_url = sys.argv[1]
else:
    test_url = "https://www.scan-manga.com/lecture-en-ligne/Return-of-the-Iron-Blooded-Hound-Chapitre-126-FR_478862.html"

print("=" * 80)
print("DÉBOGAGE DÉTAILLÉ DU SCRAPER")
print("=" * 80)
print(f"\nURL testée: {test_url}\n")

session = create_session()

try:
    response = session.get(test_url, timeout=15)
    response.raise_for_status()
    
    print(f"✅ Page chargée avec succès")
    print(f"   Status: {response.status_code}")
    print(f"   Taille: {len(response.content)} bytes")
    
    # Sauvegarder le HTML pour inspection
    with open('debug_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"   HTML sauvegardé dans: debug_page.html")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("\n" + "=" * 80)
    print("ANALYSE DES IMAGES")
    print("=" * 80)
    
    # 1. Vérifier les meta tags
    print("\n1. META TAGS:")
    meta_og_image = soup.find("meta", {"property": "og:image"})
    if meta_og_image:
        print(f"   og:image = {meta_og_image.get('content')}")
    else:
        print("   ❌ Pas de og:image")
    
    meta_twitter_image = soup.find("meta", {"name": "twitter:image"})
    if meta_twitter_image:
        print(f"   twitter:image = {meta_twitter_image.get('content')}")
    else:
        print("   ❌ Pas de twitter:image")
    
    # 2. Chercher toutes les images
    print("\n2. TOUTES LES IMAGES (<img>):")
    all_imgs = soup.find_all('img')
    print(f"   Total: {len(all_imgs)} images trouvées\n")
    
    for i, img in enumerate(all_imgs[:20], 1):  # Limiter à 20 premières images
        print(f"   Image #{i}:")
        print(f"      src: {img.get('src', 'N/A')}")
        print(f"      data-src: {img.get('data-src', 'N/A')}")
        print(f"      data-lazy-src: {img.get('data-lazy-src', 'N/A')}")
        print(f"      alt: {img.get('alt', 'N/A')}")
        print(f"      class: {img.get('class', 'N/A')}")
        print()
    
    # 3. Chercher des divs avec background-image
    print("\n3. ÉLÉMENTS AVEC STYLE BACKGROUND-IMAGE:")
    elements_with_bg = soup.find_all(style=lambda value: value and 'background-image' in value)
    print(f"   Total: {len(elements_with_bg)} éléments trouvés\n")
    
    for i, elem in enumerate(elements_with_bg[:10], 1):
        print(f"   Élément #{i}:")
        print(f"      Tag: {elem.name}")
        print(f"      Style: {elem.get('style')}")
        print(f"      Class: {elem.get('class', 'N/A')}")
        print()
    
    # 4. Chercher des sélecteurs spécifiques
    print("\n4. SÉLECTEURS SPÉCIFIQUES:")
    selectors = [
        ".manga-cover img",
        ".post-thumbnail img",
        ".entry-thumb img",
        ".wp-post-image",
        ".cover-image img",
        "img[class*='cover']",
        "img[class*='poster']",
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            print(f"   ✅ '{selector}': {len(elements)} trouvé(s)")
            for elem in elements[:2]:
                print(f"      → src: {elem.get('src', 'N/A')}")
        else:
            print(f"   ❌ '{selector}': aucun")
    
    # 5. Chercher dans les scripts JSON-LD
    print("\n5. SCRIPTS JSON-LD:")
    scripts = soup.find_all('script', type='application/ld+json')
    print(f"   Total: {len(scripts)} scripts trouvés")
    
    if scripts:
        import json
        for i, script in enumerate(scripts, 1):
            try:
                data = json.loads(script.string)
                print(f"\n   Script #{i}:")
                print(f"      Type: {data.get('@type', 'N/A')}")
                if 'image' in data:
                    print(f"      Image: {data['image']}")
            except:
                print(f"   Script #{i}: Erreur de parsing")
    
    print("\n" + "=" * 80)
    print("FIN DU DÉBOGAGE")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
