"""Script de test simple pour le scraper"""
from scraper.scraper import scrape_manga_info

# URL de test
test_url = "https://www.scan-manga.com/lecture-en-ligne/One-Piece-Chapitre-1000-FR_123456.html"

print("=" * 80)
print("TEST DU SCRAPER")
print("=" * 80)
print(f"\nURL de test : {test_url}\n")

result = scrape_manga_info(test_url)

print("\nRÉSULTAT :")
print("-" * 80)
for key, value in result.items():
    if key == 'resume' and value:
        print(f"{key:20} : {value[:100]}...")
    else:
        print(f"{key:20} : {value}")

print("\n" + "=" * 80)

if result.get('image') == "https://via.placeholder.com/300x420?text=Manga":
    print("⚠️  Image placeholder utilisée (site probablement bloqué)")
else:
    print("✅ Image réelle trouvée")
