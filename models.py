from sqlalchemy import (
    Column, Integer, String, Float, Date, Text, LargeBinary
)
from sqlalchemy.sql import func
from database import Base


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
    nom_complet = Column(Text)
    nom_utilisateur = Column(Text)
    mot_de_passe = Column(Text)
    adresse = Column(Text)
    telephone = Column(Text)
    email = Column(Text)
    role = Column(Text)
    action = Column(Text)


class Monnaie(Base):
    __tablename__ = "monnaies"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
    nom = Column(Text)
    sigle = Column(Text)
    action = Column(Text)


class Client(Base):
    __tablename__ = "clients"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
    nom = Column(Text)
    type_client = Column(Text)
    adresse = Column(Text)
    telephone = Column(Text)
    email = Column(Text)
    action = Column(Text)


class Dossier(Base):
    __tablename__ = "dossiers"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
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
    type_bl = Column(Text)
    action = Column(Text)


class Conteneur(Base):
    __tablename__ = "conteneurs"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
    dossier_uuid = Column(Text)
    numero_conteneur = Column(Text)
    dimension = Column(Text)
    date_sorti_port = Column(Date)
    nom_transporteur = Column(Text)
    marque_camion = Column(Text)
    numero_plaque = Column(Text)
    nom_chauffeur = Column(Text)
    numero_chauffeur = Column(Text)
    lieu_dechargement = Column(Text)
    date_arriver_lieu_dechargement = Column(Date)
    date_dechargement = Column(Date)
    date_depart_retout_port = Column(Date)
    date_retour_port = Column(Date)
    action = Column(Text)


class DetailConteneur(Base):
    __tablename__ = "detail_conteneurs"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
    conteneur_uuid = Column(Text)
    nom_article = Column(Text)
    quantite = Column(Float)
    unite_mesure = Column(Text)
    action = Column(Text)


class Interchange(Base):
    __tablename__ = "interchange"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
    conteneur_uuid = Column(Text)
    scan = Column(LargeBinary)
    page = Column(Integer)
    nom_fichier = Column(Text)
    action = Column(Text)


class DepotArgent(Base):
    __tablename__ = "depot_argent_makoso"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
    monnaie_uuid = Column(Text)
    montant = Column(Float)
    libelle = Column(Text)
    observation = Column(Text)
    date_paiement = Column(Date)
    source_uuid = Column(Text)
    agent = Column(Text)
    action = Column(Text)


class DepotArgentMarinasTrans(Base):
    __tablename__ = "depot_argent_marina_trans"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
    monnaie_uuid = Column(Text)
    montant = Column(Float)
    libelle = Column(Text)
    observation = Column(Text)
    date_paiement = Column(Date)
    source_uuid = Column(Text)
    agent = Column(Text)
    action = Column(Text)


class Depense(Base):
    __tablename__ = "depenses_makoso"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
    montant = Column(Float)
    libelle = Column(Text)
    observation = Column(Text)
    date = Column(Date)
    valide = Column(Integer)
    date_validation = Column(Date)
    validateur_uuid = Column(Text)
    monnaie_uuid = Column(Text)
    deja_executer = Column(Integer, default=0)
    dossier_uuid = Column(Text)
    action = Column(Text)


class DepenseMarinasTrans(Base):
    __tablename__ = "depenses_marina_trans"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
    montant = Column(Float)
    libelle = Column(Text)
    observation = Column(Text)
    date = Column(Date)
    valide = Column(Integer)
    date_validation = Column(Date)
    validateur_uuid = Column(Text)
    monnaie_uuid = Column(Text)
    type_depense = Column(Text)
    origine_uuid = Column(Text)
    deja_executer = Column(Integer, default=0)
    action = Column(Text)


class ScanBl(Base):
    __tablename__ = "scan_bl"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
    dossier_uuid = Column(Text)
    scan = Column(LargeBinary)
    page = Column(Integer)
    nom_fichier = Column(Text)


class ScanVoyage(Base):
    __tablename__ = "scan_voyage"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
    dossier_uuid = Column(Text)
    scan = Column(LargeBinary)
    page = Column(Integer)
    nom_fichier = Column(Text)


class Camion(Base):
    __tablename__ = "camions"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
    marque = Column(Text)
    plaque = Column(Text)
    modele = Column(Text)
    capacite = Column(Text)
    action = Column(Text)


class ChauffeurConvoyeur(Base):
    __tablename__ = "chauffeurs_convoyeurs"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
    nom = Column(Text)
    telephone = Column(Text)
    adresse = Column(Text)
    date_engagement = Column(Date)
    fonction = Column(Text)
    action = Column(Text)


class Voyage(Base):
    __tablename__ = "voyages"

    uuid = Column(Text)
    id = Column(Integer)
    sync = Column(Integer, primary_key=True)
    numero_voyage = Column(Text)
    date_voyage = Column(Text)
    lieu_depart = Column(Text)
    lieu_destination = Column(Text)
    montant_convenu = Column(Float)
    client_uuid = Column(Text)
    monnaie_uuid = Column(Text)
    statut = Column(Text)
    camion_uuid = Column(Text)
    chauffeur_uuid = Column(Text)
    convoyeur_uuid = Column(Text)
    action = Column(Text)


class Solde(Base):
    __tablename__ = "solde"

    uuid = Column(Text, primary_key=True)
    id = Column(Integer)
    sync = Column(Integer, default=0)
    monnaie_uuid = Column(Text)
    montant = Column(Float)
    date_cloture = Column(Date)
    nom_company = Column(Text)
