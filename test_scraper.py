"""Script de test pour déboguer le scraping d'images"""
from scraper.scraper import scrape_manga_info

# URL de test - remplacez par votre URL
test_url = "https://www.scan-manga.com/lecture-en-ligne/Return-of-the-Iron-Blooded-Hound-Chapitre-126-FR_478862.html"

print("=" * 80)
print("TEST DU SCRAPER")
print("=" * 80)
print(f"\nURL testée: {test_url}\n")

result = scrape_manga_info(test_url)

print("\n" + "=" * 80)
print("RÉSULTAT FINAL")
print("=" * 80)
print(f"Titre: {result.get('titre')}")
print(f"Chapitre: {result.get('chapitre')}")
print(f"Image: {result.get('image')}")
print(f"Résumé: {result.get('resume')[:100] if result.get('resume') else 'Aucun'}...")
print(f"Source: {result.get('source')}")
print("\n" + "=" * 80)

# Vérifier si c'est le placeholder
if result.get('image') == "https://via.placeholder.com/300x420?text=Manga":
    print("⚠️  ATTENTION: Image placeholder utilisée - l'image réelle n'a pas été trouvée")
else:
    print("✅ Image réelle trouvée!")
