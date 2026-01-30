class Manga(db.Model):
    __tablename__ = "mangas"
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    dernier_chapitre = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    image_couverture = db.Column(db.String(500), nullable=True)
    resume = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(100), nullable=True)  # scan-manga / anime-sama
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    date_maj = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Manga {self.titre} ch.{self.dernier_chapitre}>"

with app.app_context():
    db.create_all()