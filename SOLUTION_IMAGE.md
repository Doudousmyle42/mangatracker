# Solution pour récupérer les images de manga

## Problème identifié
Le site **scan-manga.com** bloque les requêtes automatiques (erreur 403 Forbidden), ce qui empêche le scraper de récupérer les pages et donc les images.

## Solutions possibles

### Solution 1: Scraping manuel (RECOMMANDÉ pour l'instant)

1. **Ouvrez l'URL dans votre navigateur:**
   ```
   https://www.scan-manga.com/lecture-en-ligne/Eleceed-Chapitre-363-FR_498341.html
   ```

2. **Sauvegardez la page:**
   - Appuyez sur `Ctrl+S`
   - Sauvegardez le fichier HTML dans le dossier du projet (ex: `eleceed.html`)

3. **Exécutez le script de scraping manuel:**
   ```bash
   python manual_scraper.py eleceed.html "https://www.scan-manga.com/lecture-en-ligne/Eleceed-Chapitre-363-FR_498341.html"
   ```

### Solution 2: Utiliser Selenium (automatisation de navigateur)

Le site bloque les requêtes HTTP simples mais pas les navigateurs réels. On peut utiliser Selenium:

1. **Installer Selenium:**
   ```bash
   pip install selenium webdriver-manager
   ```

2. **J'ai créé un scraper avec Selenium** (voir `scraper_selenium.py`)

### Solution 3: Entrer l'image manuellement

Si vous voulez juste tester l'application:

1. Ouvrez l'URL dans votre navigateur
2. Clic droit sur l'image de couverture → "Copier l'adresse de l'image"
3. Collez cette URL dans votre application

### Solution 4: Utiliser une API de manga

Certaines APIs publiques fournissent des informations sur les mangas:
- **MyAnimeList API**
- **AniList API**
- **MangaDex API**

## Quelle solution préférez-vous ?

1. **Scraping manuel** (simple mais nécessite de sauvegarder chaque page)
2. **Selenium** (automatique mais plus lourd)
3. **API externe** (fiable mais peut ne pas avoir tous les mangas)
4. **Saisie manuelle** (pour tester rapidement)

Dites-moi quelle approche vous préférez et je l'implémenterai !
