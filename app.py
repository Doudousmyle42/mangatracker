from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from scraper.scraper import scrape_manga_info

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "manga.db")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev-secret-change-me-in-production"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max

db = SQLAlchemy(app)

# Modèle de données
class Manga(db.Model):
    __tablename__ = "mangas"
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    dernier_chapitre = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    image_couverture = db.Column(db.String(500), nullable=True)
    resume = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(100), nullable=True)
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    date_maj = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Manga {self.titre} ch.{self.dernier_chapitre}>"

def allowed_file(filename):
    """Vérifie si le fichier a une extension autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
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
        titre_manuel = request.form.get("titre_manuel", "").strip()
        chapitre_manuel = request.form.get("chapitre_manuel", "").strip()
        resume_manuel = request.form.get("resume_manuel", "").strip()
        
        # Gestion de l'image uploadée
        image_url = None
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Ajouter un timestamp pour éviter les collisions
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_url = url_for('static', filename=f'uploads/{filename}')
        
        # Si pas d'URL fournie, créer manuellement
        if not url and titre_manuel:
            manga = Manga(
                titre=titre_manuel,
                dernier_chapitre=chapitre_manuel or "1",
                url=request.form.get("url_lecture", "#"),
                image_couverture=image_url,
                resume=resume_manuel,
                source="Manuel",
            )
            db.session.add(manga)
            db.session.commit()
            flash(f"'{manga.titre}' ajouté manuellement à la bibliothèque !", "success")
            return redirect(url_for("index"))
        
        # Sinon, scraper l'URL
        if not url:
            flash("Merci de fournir une URL ou un titre manuel", "warning")
            return redirect(url_for("add"))
        
        try:
            data = scrape_manga_info(url)
            manga = Manga(
                titre=data.get("titre", "Manga"),
                dernier_chapitre=str(data.get("chapitre", "1")),
                url=url,
                image_couverture=image_url or data.get("image"),  # Priorité à l'image uploadée
                resume=data.get("resume"),
                source=data.get("source"),
            )
            db.session.add(manga)
            db.session.commit()
            flash(f"'{manga.titre}' ajouté à la bibliothèque !", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Erreur lors de l'ajout : {e}", "danger")
            return redirect(url_for("add"))
    
    return render_template("add.html")

@app.route("/edit/<int:manga_id>", methods=["GET", "POST"])
def edit(manga_id):
    """Éditer un manga existant"""
    manga = Manga.query.get_or_404(manga_id)
    
    if request.method == "POST":
        manga.titre = request.form.get("titre", manga.titre).strip()
        manga.dernier_chapitre = request.form.get("chapitre", manga.dernier_chapitre).strip()
        manga.url = request.form.get("url", manga.url).strip()
        manga.resume = request.form.get("resume", manga.resume)
        
        # Gestion de l'image uploadée
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                manga.image_couverture = url_for('static', filename=f'uploads/{filename}')
        
        # Option pour supprimer l'image
        if request.form.get("remove_image"):
            manga.image_couverture = None
        
        db.session.commit()
        flash("Manga mis à jour avec succès !", "success")
        return redirect(url_for("index"))
    
    return render_template("edit.html", manga=manga)

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
    """Re-scrape la page pour mettre à jour les informations"""
    manga = Manga.query.get_or_404(manga_id)
    
    try:
        data = scrape_manga_info(manga.url)
        manga.titre = data.get("titre", manga.titre)
        
        # Ne pas écraser l'image uploadée manuellement
        if not manga.image_couverture or not manga.image_couverture.startswith('/static/uploads/'):
            manga.image_couverture = data.get("image", manga.image_couverture)
        
        # Mise à jour du chapitre si supérieur
        old = manga.dernier_chapitre
        new = str(data.get("chapitre", old))
        try:
            if float(new) > float(old):
                manga.dernier_chapitre = new
        except ValueError:
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
    
    # Supprimer l'image uploadée si elle existe
    if manga.image_couverture and manga.image_couverture.startswith('/static/uploads/'):
        try:
            filename = manga.image_couverture.split('/')[-1]
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Erreur lors de la suppression de l'image : {e}")
    
    db.session.delete(manga)
    db.session.commit()
    flash("Manga supprimé.", "info")
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)