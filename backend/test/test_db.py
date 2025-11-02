from sqlalchemy import create_engine, Column, Integer, String, Text, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Configuration de la connexion à MySQL
DATABASE_URL = "mysql+pymysql://wine_user:secure_password@localhost:3306/wine_cellar"
engine = create_engine(DATABASE_URL)

# Base pour les modèles
Base = declarative_base()

# Modèle pour la table 'users'
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    cellars = relationship("Cellar", back_populates="user")

# Modèle pour la table 'cellars'
class Cellar(Base):
    __tablename__ = "cellars"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    user = relationship("User", back_populates="cellars")
    bottles = relationship("Bottle", back_populates="cellar")

# Modèle pour la table 'bottles'
class Bottle(Base):
    __tablename__ = "bottles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cellar_id = Column(Integer, ForeignKey("cellars.id"))
    name = Column(String(255), nullable=False)
    vintage = Column(Integer)
    wine_type = Column(String(100))
    region = Column(String(100))
    country = Column(String(100))
    price = Column(DECIMAL(10, 2))
    quantity = Column(Integer, default=1)
    image_url = Column(String(255))
    notes = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    cellar = relationship("Cellar", back_populates="bottles")

# Crée les tables dans la base de données (si elles n'existent pas)
Base.metadata.create_all(engine)

# Crée une session pour interagir avec la base de données
Session = sessionmaker(bind=engine)
session = Session()

# Exemple d'écriture : Ajouter un utilisateur, une cave et une bouteille
def add_sample_data():
    # Ajouter un utilisateur
    user = User(email="user@example.com", password_hash="hashed_password")
    session.add(user)
    session.commit()

    # Ajouter une cave
    cellar = Cellar(user_id=user.id, name="Ma Cave à Vin", location="Sous-sol")
    session.add(cellar)
    session.commit()

    # Ajouter une bouteille
    bottle = Bottle(
        cellar_id=cellar.id,
        name="Château Margaux",
        vintage=2015,
        wine_type="Rouge",
        region="Bordeaux",
        country="France",
        price=1200.50,
        quantity=2,
        image_url="https://example.com/chateau-margaux.jpg",
        notes="Grand cru classé de Bordeaux."
    )
    session.add(bottle)
    session.commit()
    print("Données ajoutées avec succès !")

# Exemple de lecture : Lister toutes les bouteilles
def list_bottles():
    bottles = session.query(Bottle).all()
    for bottle in bottles:
        print(f"ID: {bottle.id}, Nom: {bottle.name}, Millésime: {bottle.vintage}, Prix: {bottle.price} €")

# Exemple de lecture : Lister les caves d'un utilisateur
def list_user_cellars(user_email):
    user = session.query(User).filter_by(email=user_email).first()
    if user:
        for cellar in user.cellars:
            print(f"Cave: {cellar.name}, Localisation: {cellar.location}")
    else:
        print("Utilisateur non trouvé.")

# Exécution des exemples
if __name__ == "__main__":
    add_sample_data()
    print("\nListe des bouteilles :")
    list_bottles()
    print("\nCaves de l'utilisateur user@example.com :")
    list_user_cellars("user@example.com")

    # Ferme la session
    session.close()
