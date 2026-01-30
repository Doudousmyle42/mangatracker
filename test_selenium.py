"""Test du scraper Selenium"""
import sys

try:
    from scraper.scraper_selenium import scrape_manga_info_selenium
    
    test_url = "https://www.scan-manga.com/lecture-en-ligne/Eleceed-Chapitre-363-FR_498341.html"
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    print("=" * 80)
    print("TEST DU SCRAPER SELENIUM")
    print("=" * 80)
    print(f"\nURL: {test_url}\n")
    
    result = scrape_manga_info_selenium(test_url)
    
    print("\n" + "=" * 80)
    print("RÉSULTAT FINAL:")
    print("=" * 80)
    print(f"Titre: {result.get('titre')}")
    print(f"Chapitre: {result.get('chapitre')}")
    print(f"Image: {result.get('image')}")
    if result.get('resume'):
        print(f"Résumé: {result.get('resume')[:100]}...")
    else:
        print("Résumé: Aucun")
    print(f"Source: {result.get('source')}")
    
    print("\n" + "=" * 80)
    if result.get('image') != "https://via.placeholder.com/300x420?text=Manga":
        print("✅ SUCCESS: Image réelle trouvée!")
    else:
        print("⚠️  WARNING: Image placeholder utilisée")
    
except ImportError as e:
    print("❌ ERREUR: Selenium n'est pas installé")
    print("\nPour installer Selenium, exécutez:")
    print("  pip install selenium webdriver-manager")
    print("\nOu installez toutes les dépendances:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
