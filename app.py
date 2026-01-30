from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from urllib.parse import urlparse
from scraper.scraper import scrape_manga_info


# --- Config de base ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "manga.db")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev-secret-change-me"  # à remplacer en prod

db = SQLAlchemy(app)

# --- Modèle Manga (fusionné depuis models.py) ---
class Manga(db.Model):
    __tablename__ = "mangas"
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    dernier_chapitre = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    cover_volume_manga = db.Column(db.String(500), nullable=True)
    resume = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(100), nullable=True)  # scan-manga / anime-sama
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    date_maj = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Manga {self.titre} ch.{self.dernier_chapitre}>"


# --- Routes fusionnées depuis routes.py ---
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
            data = scrape_manga_info(url)
            manga = Manga(
                titre=data.get("titre", "Manga"),
                dernier_chapitre=str(data.get("chapitre", "1")),
                url=url,
                cover_volume_manga=data.get("image"),
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
        data = scrape_manga_info(manga.url)
        manga.titre = data.get("titre", manga.titre)
        manga.cover_volume_manga = data.get("image", manga.cover_volume_manga)
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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # <-- Ajoute cette ligne
    app.run(debug=True)