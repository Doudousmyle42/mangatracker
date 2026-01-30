"""Analyse un fichier HTML sauvegardé manuellement"""
import sys
from bs4 import BeautifulSoup
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python analyze_html.py <fichier.html>")
    sys.exit(1)

html_file = sys.argv[1]

if not Path(html_file).exists():
    print(f"❌ Fichier non trouvé: {html_file}")
    sys.exit(1)

print("=" * 80)
print(f"ANALYSE DU FICHIER: {html_file}")
print("=" * 80)

with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

print("\n1. TITRE DE LA PAGE:")
title = soup.find('title')
if title:
    print(f"   {title.get_text()}")

print("\n2. META TAGS IMAGES:")
meta_tags = [
    ("og:image", {"property": "og:image"}),
    ("twitter:image", {"name": "twitter:image"}),
]

for name, attrs in meta_tags:
    meta = soup.find("meta", attrs)
    if meta:
        print(f"   {name}: {meta.get('content')}")
    else:
        print(f"   {name}: ❌ Non trouvé")

print("\n3. TOUTES LES IMAGES:")
all_imgs = soup.find_all('img')
print(f"   Total: {len(all_imgs)} images\n")

for i, img in enumerate(all_imgs[:30], 1):
    print(f"   Image #{i}:")
    print(f"      src: {img.get('src', 'N/A')}")
    if img.get('data-src'):
        print(f"      data-src: {img.get('data-src')}")
    if img.get('data-lazy-src'):
        print(f"      data-lazy-src: {img.get('data-lazy-src')}")
    if img.get('alt'):
        print(f"      alt: {img.get('alt')}")
    if img.get('class'):
        print(f"      class: {img.get('class')}")
    print()

print("\n4. ÉLÉMENTS AVEC BACKGROUND-IMAGE:")
elements_with_bg = soup.find_all(style=lambda value: value and 'background-image' in value)
print(f"   Total: {len(elements_with_bg)}\n")

for i, elem in enumerate(elements_with_bg[:10], 1):
    print(f"   Élément #{i} ({elem.name}):")
    print(f"      style: {elem.get('style')}")
    print()

print("\n5. SÉLECTEURS SPÉCIFIQUES:")
selectors = [
    ".manga-cover img",
    ".post-thumbnail img",
    ".entry-thumb img",
    ".wp-post-image",
    ".cover-image img",
    ".manga-poster img",
    "img[class*='cover']",
    "img[class*='poster']",
    "img[class*='thumb']",
]

for selector in selectors:
    elements = soup.select(selector)
    if elements:
        print(f"   ✅ '{selector}': {len(elements)} trouvé(s)")
        for elem in elements[:2]:
            print(f"      → {elem.get('src', elem.get('data-src', 'N/A'))}")
    else:
        print(f"   ❌ '{selector}': aucun")

print("\n" + "=" * 80)
print("RECOMMANDATIONS:")
print("=" * 80)

# Trouver la meilleure image candidate
print("\nRecherche de la meilleure image de couverture...")

candidates = []
for img in all_imgs:
    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
    if src:
        score = 0
        src_lower = src.lower()
        
        # Mots-clés positifs
        if any(kw in src_lower for kw in ['cover', 'poster', 'thumb', 'manga']):
            score += 10
        
        # Classes
        classes = ' '.join(img.get('class', [])).lower()
        if any(kw in classes for kw in ['cover', 'poster', 'thumb']):
            score += 5
        
        # Alt text
        alt = (img.get('alt') or '').lower()
        if any(kw in alt for kw in ['cover', 'poster', 'manga']):
            score += 3
        
        if score > 0:
            candidates.append((score, src, img))

if candidates:
    candidates.sort(reverse=True, key=lambda x: x[0])
    print(f"\n✅ {len(candidates)} image(s) candidate(s) trouvée(s):")
    for i, (score, src, img) in enumerate(candidates[:5], 1):
        print(f"\n   #{i} (score: {score}):")
        print(f"      URL: {src}")
        print(f"      Classes: {img.get('class', 'N/A')}")
        print(f"      Alt: {img.get('alt', 'N/A')}")
else:
    print("\n❌ Aucune image candidate trouvée avec les critères actuels")
    print("\nVoici les 5 premières images de la page:")
    for i, img in enumerate(all_imgs[:5], 1):
        src = img.get('src') or img.get('data-src') or 'N/A'
        print(f"   #{i}: {src}")
