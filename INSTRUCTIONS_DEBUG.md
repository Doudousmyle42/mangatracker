# Instructions pour déboguer le problème d'image

## Option 1: Sauvegarder le HTML manuellement

1. Ouvrez l'URL du manga dans votre navigateur
2. Faites **Ctrl+S** pour sauvegarder la page complète
3. Placez le fichier HTML dans le dossier du projet sous le nom `page_test.html`
4. Exécutez: `python analyze_html.py page_test.html`

## Option 2: Inspecter l'image dans le navigateur

1. Ouvrez l'URL du manga dans votre navigateur
2. Faites **clic droit** sur l'image de couverture du manga
3. Sélectionnez **"Inspecter l'élément"** ou **"Inspecter"**
4. Copiez le code HTML de la balise `<img>` ou du conteneur de l'image
5. Partagez-moi ce code HTML

## Option 3: Tester avec une autre URL

Si vous avez une autre URL de manga qui fonctionne, testez avec:
```bash
python debug_scraper.py "VOTRE_URL_ICI"
```

## Problèmes possibles identifiés

Le site scan-manga.com semble bloquer les requêtes automatiques. Voici les solutions possibles:

1. **L'image est chargée en JavaScript** (lazy loading)
2. **L'image nécessite des cookies/session**
3. **L'image est dans un attribut non-standard** (data-src, data-lazy-src, etc.)
4. **L'image est en background-image CSS**
5. **Le site détecte les bots et bloque l'accès**
