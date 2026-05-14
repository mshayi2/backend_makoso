from sqlalchemy import (
    Column, Integer, String, Float, Date, Text, LargeBinary
)
from sqlalchemy.sql import func
from database import Base


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    uuid = Column(Text, primary_key=True)
    id = Column(Integer)
    sync = Column(Integer, default=0)
    nom_complet = Column(Text)
    nom_utilisateur = Column(Text)
    mot_de_passe = Column(Text)
    adresse = Column(Text)
    telephone = Column(Text)
    email = Column(Text)
    role = Column(Text)


class Monnaie(Base):
    __tablename__ = "monnaies"

    uuid = Column(Text, primary_key=True)
    id = Column(Integer)
    sync = Column(Integer, default=0)
    nom = Column(Text)
    sigle = Column(Text)


class Client(Base):
    __tablename__ = "clients"

    uuid = Column(Text, primary_key=True)
    id = Column(Integer)
    sync = Column(Integer, default=0)
    nom = Column(Text)
    adresse = Column(Text)
    telephone = Column(Text)
    email = Column(Text)


class Dossier(Base):
    __tablename__ = "dossiers"

    uuid = Column(Text, primary_key=True)
    id = Column(Integer)
    sync = Column(Integer, default=0)
    client_uuid = Column(Text)
    numero_bl = Column(Text)
    port_chargement = Column(Text)
    port_destination = Column(Text)
    nature_marchandise = Column(Text)
    date_arrivee_pn = Column(Date)
    date_arrivee_matadi = Column(Date)
    date_paiement_30_draft = Column(Date)
    date_paiement_30_pn = Column(Date)
    date_paiement_40_matadi = Column(Date)
    montant_convenu = Column(Float)
    statut = Column(Text)
    date_creation = Column(Date, server_default=func.current_date())


class Conteneur(Base):
    __tablename__ = "conteneurs"

    uuid = Column(Text, primary_key=True)
    id = Column(Integer)
    sync = Column(Integer, default=0)
    dossier_uuid = Column(Text)
    numero_conteneur = Column(Text)
    dimension = Column(Text)


class DetailConteneur(Base):
    __tablename__ = "detail_conteneurs"

    uuid = Column(Text, primary_key=True)
    id = Column(Integer)
    sync = Column(Integer, default=0)
    conteneur_uuid = Column(Text)
    nom_article = Column(Text)
    quantite = Column(Float)
    unite_mesure = Column(Text)


class Interchange(Base):
    __tablename__ = "interchange"

    uuid = Column(Text, primary_key=True)
    id = Column(Integer)
    sync = Column(Integer, default=0)
    conteneur_uuid = Column(Text)
    scan = Column(LargeBinary)


class DepotArgent(Base):
    __tablename__ = "depot_argent"

    uuid = Column(Text, primary_key=True)
    id = Column(Integer)
    sync = Column(Integer, default=0)
    monnaie_uuid = Column(Text)
    montant = Column(Float)
    libelle = Column(Text)
    observation = Column(Text)
    date_paiement = Column(Date)
    source_uuid = Column(Text)
    agent = Column(Text)


class Depense(Base):
    __tablename__ = "depenses"

    uuid = Column(Text, primary_key=True)
    id = Column(Integer)
    sync = Column(Integer, default=0)
    montant = Column(Float)
    libelle = Column(Text)
    observation = Column(Text)
    date = Column(Date)
    valide = Column(Integer)
    date_validation = Column(Date)
    validateur_uuid = Column(Text)
    monnaie_uuid = Column(Text)


class Camion(Base):
    __tablename__ = "camions"

    uuid = Column(Text, primary_key=True)
    id = Column(Integer)
    sync = Column(Integer, default=0)
    marque = Column(Text)
    plaque = Column(Text)
    modele = Column(Text)
    capacite = Column(Text)


class ChauffeurConvoyeur(Base):
    __tablename__ = "chauffeurs_convoyeurs"

    uuid = Column(Text, primary_key=True)
    id = Column(Integer)
    sync = Column(Integer, default=0)
    nom = Column(Text)
    telephone = Column(Text)
    adresse = Column(Text)
    date_engagement = Column(Date)
    fonction = Column(Text)


class Voyage(Base):
    __tablename__ = "voyages"

    uuid = Column(Text, primary_key=True)
    id = Column(Integer)
    sync = Column(Integer, default=0)
    numero_voyage = Column(Text)
    date_voyage = Column(Text)
    lieu_depart = Column(Text)
    lieu_destination = Column(Text)
    montant_convenu = Column(Float)
    monnaie_uuid = Column(Text)
    statut = Column(Text)
    camion_uuid = Column(Text)
    chauffeur_uuid = Column(Text)
    convoyeur_uuid = Column(Text)
