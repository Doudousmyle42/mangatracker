"""
Script pour scraper manuellement une page sauvegardée
Usage: 
1. Ouvrez l'URL du manga dans votre navigateur
2. Ctrl+S pour sauvegarder la page complète
3. Placez le fichier HTML dans ce dossier
4. Exécutez: python manual_scraper.py <fichier.html> <url_originale>
"""
import sys
from bs4 import BeautifulSoup
from pathlib import Path
from scraper.scraper import (
    _extract_title_from_url, 
    _extract_chapter_from_url,
    _is_valid_manga_image,
    _score_manga_image,
    _clean_text,
    PLACEHOLDER_IMG
)
from urllib.parse import urljoin

def scrape_from_file(html_file, original_url):
    """Scrape depuis un fichier HTML sauvegardé"""
    
    if not Path(html_file).exists():
        print(f"❌ Fichier non trouvé: {html_file}")
        return None
    
    print(f"📄 Lecture du fichier: {html_file}")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extraire le titre
    title = _extract_title_from_url(original_url)
    print(f"✅ Titre: {title}")
    
    # Extraire le chapitre
    chapitre = _extract_chapter_from_url(original_url)
    print(f"✅ Chapitre: {chapitre}")
    
    # Chercher l'image
    img = None
    
    # 1. Meta tags
    print("\n🔍 Recherche de l'image...")
    meta_og = soup.find("meta", {"property": "og:image"})
    if meta_og:
        candidate = meta_og.get("content")
        if candidate:
            img = candidate if candidate.startswith('http') else urljoin(original_url, candidate)
            print(f"   ✅ Trouvée via og:image: {img}")
    
    # 2. Recherche dans toutes les images
    if not img:
        print("   Recherche dans toutes les images...")
        all_imgs = soup.find_all('img')
        print(f"   {len(all_imgs)} images trouvées")
        
        valid_images = []
        for img_tag in all_imgs:
            for attr in ['src', 'data-src', 'data-lazy-src', 'data-original']:
                candidate = img_tag.get(attr)
                if candidate:
                    full_url = candidate if candidate.startswith('http') else urljoin(original_url, candidate)
                    
                    if _is_valid_manga_image(full_url):
                        score = _score_manga_image(full_url, img_tag)
                        valid_images.append((score, full_url))
                        print(f"   Image valide (score: {score}): {full_url[:80]}...")
        
        if valid_images:
            valid_images.sort(reverse=True, key=lambda x: x[0])
            img = valid_images[0][1]
            print(f"   ✅ Meilleure image: {img}")
    
    # 3. Résumé
    resume = None
    resume_selectors = [
        ".manga-summary",
        ".manga-description",
        ".synopsis",
        ".entry-content p",
    ]
    
    for selector in resume_selectors:
        element = soup.select_one(selector)
        if element:
            candidate = _clean_text(element.get_text())
            if candidate and len(candidate) > 30:
                resume = candidate[:500]
                break
    
    if not img:
        img = PLACEHOLDER_IMG
        print("   ⚠️  Aucune image trouvée, utilisation du placeholder")
    
    result = {
        "titre": title or "Manga Inconnu",
        "chapitre": chapitre,
        "image": img,
        "resume": resume,
        "source": "scan-manga"
    }
    
    print("\n" + "=" * 80)
    print("RÉSULTAT:")
    print("=" * 80)
    for key, value in result.items():
        if key == 'resume' and value:
            print(f"{key}: {value[:100]}...")
        else:
            print(f"{key}: {value}")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python manual_scraper.py <fichier.html> <url_originale>")
        print("\nExemple:")
        print('  python manual_scraper.py page.html "https://www.scan-manga.com/lecture-en-ligne/Eleceed-Chapitre-363-FR_498341.html"')
        sys.exit(1)
    
    html_file = sys.argv[1]
    original_url = sys.argv[2]
    
    scrape_from_file(html_file, original_url)
