from types import SimpleNamespace

@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    if q:
        mangas = Manga.query.filter(Manga.titre.ilike(f"%{q}%")).order_by(Manga.date_maj.desc()).all()
    else:
        mangas = Manga.query.order_by(Manga.date_maj.desc()).all()
    return render_template("index.html", mangas=mangas, q=q)

@app.route("/add", methods=["GET", "POST"]) 
def add():
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url:
            flash("Merci de fournir une URL", "warning")
            return redirect(url_for("add"))
        try:
            from __main__ import scrape_manga_info  # import interne (même fichier)
            data = scrape_manga_info(url)
            manga = Manga(
                titre=data.get("titre", "Manga"),
                dernier_chapitre=str(data.get("chapitre", "1")),
                url=url,
                image_couverture=data.get("image"),
                resume=data.get("resume"),
                source=data.get("source"),
            )
            db.session.add(manga)
            db.session.commit()
            flash(f"‘{manga.titre}’ ajouté à la bibliothèque !", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Erreur lors de l'ajout : {e}", "danger")
            return redirect(url_for("add"))
    return render_template("add.html")

@app.route("/update/<int:manga_id>", methods=["POST"]) 
def update(manga_id):
    manga = Manga.query.get_or_404(manga_id)
    nouveau_chap = request.form.get("chapitre", "").strip()
    if not nouveau_chap:
        flash("Veuillez saisir un numéro de chapitre.", "warning")
        return redirect(url_for("index"))
    manga.dernier_chapitre = nouveau_chap
    db.session.commit()
    flash("Chapitre mis à jour !", "success")
    return redirect(url_for("index"))

@app.route("/refresh/<int:manga_id>", methods=["POST"]) 
def refresh(manga_id):
    """Re-scrape la page d'origine pour mettre à jour titre/image/chapitre.
    Utile si la source a changé ou si un nouveau chapitre est détecté.
    """
    manga = Manga.query.get_or_404(manga_id)
    try:
        from __main__ import scrape_manga_info
        data = scrape_manga_info(manga.url)
        manga.titre = data.get("titre", manga.titre)
        manga.image_couverture = data.get("image", manga.image_couverture)
        # On met à jour le chapitre seulement si supérieur (heuristique simple)
        old = manga.dernier_chapitre
        new = str(data.get("chapitre", old))
        try:
            if float(new) > float(old):
                manga.dernier_chapitre = new
        except ValueError:
            # si non numérique, on remplace, au pire l'utilisateur corrigera
            manga.dernier_chapitre = new
        manga.resume = data.get("resume", manga.resume)
        manga.source = data.get("source", manga.source)
        db.session.commit()
        flash("Manga rafraîchi avec succès !", "success")
    except Exception as e:
        flash(f"Erreur lors du rafraîchissement : {e}", "danger")
    return redirect(url_for("index"))

@app.route("/delete/<int:manga_id>", methods=["POST"]) 
def delete(manga_id):
    manga = Manga.query.get_or_404(manga_id)
    db.session.delete(manga)
    db.session.commit()
    flash("Manga supprimé.", "info")
    return redirect(url_for("index"))