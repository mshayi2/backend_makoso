import uuid as uuid_lib
from contextlib import asynccontextmanager
from typing import Dict, List, Any
from datetime import date, datetime

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import select, inspect, func, text, Date as SADate

from database import engine, Base, AsyncSessionLocal
from models import (
    Monnaie, Utilisateur, Client, Dossier, Conteneur, DetailConteneur,
    Interchange, DepotArgent, DepotArgentMarinasTrans,
    Depense, DepenseMarinasTrans, Camion, ChauffeurConvoyeur, Voyage
)

TABLE_MAP = {
    "utilisateurs": Utilisateur,
    "monnaies": Monnaie,
    "clients": Client,
    "dossiers": Dossier,
    "conteneurs": Conteneur,
    "detail_conteneurs": DetailConteneur,
    "interchange": Interchange,
    "depot_argent_makoso": DepotArgent,
    "depot_argent_marina_trans": DepotArgentMarinasTrans,
    "depenses_makoso": Depense,
    "depenses_marina_trans": DepenseMarinasTrans,
    "camions": Camion,
    "chauffeurs_convoyeurs": ChauffeurConvoyeur,
    "voyages": Voyage,
}


class TableSync(BaseModel):
    table_name: str
    sync: int


class GetDataRequest(BaseModel):
    tables: List[TableSync]


class PostDataRequest(BaseModel):
    table_name: str
    records: List[Dict[str, Any]]


MONNAIES_INITIALES = [
    ("Franc Congolais", "FC"),
    ("Dollar Américain", "USD"),
    ("Euro", "EUR"),
]


async def migrer_clients():
    async with engine.begin() as conn:
        def get_columns(sync_conn):
            insp = inspect(sync_conn)
            return {col["name"] for col in insp.get_columns("clients")}

        colonnes_existantes = await conn.run_sync(get_columns)

        if "type_client" not in colonnes_existantes:
            await conn.execute(text("ALTER TABLE clients ADD COLUMN type_client TEXT"))


async def migrer_voyages():
    async with engine.begin() as conn:
        def get_columns(sync_conn):
            insp = inspect(sync_conn)
            return {col["name"] for col in insp.get_columns("voyages")}

        colonnes_existantes = await conn.run_sync(get_columns)

        if "client_uuid" not in colonnes_existantes:
            await conn.execute(text("ALTER TABLE voyages ADD COLUMN client_uuid TEXT"))


async def migrer_depot_argent_et_depenses():
    async with engine.begin() as conn:
        def table_exists(sync_conn, table_name):
            insp = inspect(sync_conn)
            return table_name in insp.get_table_names()

        # depot_argent → depot_argent_makoso
        existe_depot = await conn.run_sync(lambda c: table_exists(c, "depot_argent"))
        if existe_depot:
            existe_makoso = await conn.run_sync(lambda c: table_exists(c, "depot_argent_makoso"))
            if not existe_makoso:
                await conn.execute(text("ALTER TABLE depot_argent RENAME TO depot_argent_makoso"))

        # Créer depot_argent_marina_trans si absent
        existe_marina = await conn.run_sync(lambda c: table_exists(c, "depot_argent_marina_trans"))
        if not existe_marina:
            await conn.execute(text("""
                CREATE TABLE depot_argent_marina_trans AS
                SELECT * FROM depot_argent_makoso WHERE 1=0
            """))
            await conn.execute(text(
                "ALTER TABLE depot_argent_marina_trans ADD PRIMARY KEY (sync)"
            ))

        # depenses → depenses_makoso
        existe_depenses = await conn.run_sync(lambda c: table_exists(c, "depenses"))
        if existe_depenses:
            existe_dep_makoso = await conn.run_sync(lambda c: table_exists(c, "depenses_makoso"))
            if not existe_dep_makoso:
                await conn.execute(text("ALTER TABLE depenses RENAME TO depenses_makoso"))

        # Créer depenses_marina_trans si absent
        existe_dep_marina = await conn.run_sync(lambda c: table_exists(c, "depenses_marina_trans"))
        if not existe_dep_marina:
            await conn.execute(text("""
                CREATE TABLE depenses_marina_trans AS
                SELECT * FROM depenses_makoso WHERE 1=0
            """))
            await conn.execute(text(
                "ALTER TABLE depenses_marina_trans ADD PRIMARY KEY (sync)"
            ))
            await conn.execute(text(
                "ALTER TABLE depenses_marina_trans ADD COLUMN type_depense TEXT"
            ))
            await conn.execute(text(
                "ALTER TABLE depenses_marina_trans ADD COLUMN origine_uuid TEXT"
            ))


async def migrer_conteneurs():
    NOUVEAUX_CHAMPS = [
        ("date_sorti_port", "DATE"),
        ("nom_transporteur", "TEXT"),
        ("marque_camion", "TEXT"),
        ("numero_plaque", "TEXT"),
        ("nom_chauffeur", "TEXT"),
        ("numero_chauffeur", "TEXT"),
        ("lieu_dechargement", "TEXT"),
        ("date_arriver_lieu_dechargement", "DATE"),
        ("date_dechargement", "DATE"),
        ("date_depart_retout_port", "DATE"),
        ("date_retour_port", "DATE"),
    ]

    async with engine.begin() as conn:
        def get_columns(sync_conn):
            insp = inspect(sync_conn)
            return {col["name"] for col in insp.get_columns("conteneurs")}

        colonnes_existantes = await conn.run_sync(get_columns)

        for nom_col, type_col in NOUVEAUX_CHAMPS:
            if nom_col not in colonnes_existantes:
                await conn.execute(
                    text(f'ALTER TABLE conteneurs ADD COLUMN "{nom_col}" {type_col}')
                )


async def creer_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seeder_monnaies():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Monnaie))
        if result.scalars().first() is not None:
            return

        for i, (nom, sigle) in enumerate(MONNAIES_INITIALES, start=1):
            monnaie = Monnaie(
                uuid=str(uuid_lib.uuid4()),
                id=i,
                sync=i,
                nom=nom,
                sigle=sigle,
            )
            session.add(monnaie)

        await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await creer_tables()
    await migrer_clients()
    await migrer_voyages()
    await migrer_depot_argent_et_depenses()
    await migrer_conteneurs()
    await seeder_monnaies()
    yield
    await engine.dispose()


app = FastAPI(title="Makoso API", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Makoso API opérationnelle"}


def row_to_dict(row) -> Dict[str, Any]:
    result = {}
    for col in inspect(row.__class__).mapper.column_attrs:
        value = getattr(row, col.key)
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        elif isinstance(value, bytes):
            value = value.hex()
        result[col.key] = value
    return result


@app.post("/get_data")
async def get_data(request: GetDataRequest) -> Dict[str, List[Dict[str, Any]]]:
    response: Dict[str, List[Dict[str, Any]]] = {}

    async with AsyncSessionLocal() as session:
        for entry in request.tables:
            model = TABLE_MAP.get(entry.table_name)
            if model is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Table inconnue : {entry.table_name}"
                )
            result = await session.execute(
                select(model).where(model.sync > entry.sync)
            )
            rows = result.scalars().all()
            if entry.table_name == "interchange":
                response[entry.table_name] = [
                    {k: v for k, v in row_to_dict(r).items() if k != "scan"}
                    for r in rows
                ]
            else:
                response[entry.table_name] = [row_to_dict(r) for r in rows]

    return response


def determine_action(sync: int, id_val: int) -> str:
    if sync == 0:
        return "I"
    elif id_val > 0 and sync < 0:
        return f"U|{abs(sync)}"
    elif id_val < 0 and sync < 0:
        return f"D|{abs(id_val)}|{abs(sync)}"
    return ""


@app.post("/post_data")
async def post_data(request: PostDataRequest) -> List[Dict[str, Any]]:
    model = TABLE_MAP.get(request.table_name)
    if model is None:
        raise HTTPException(status_code=400, detail=f"Table inconnue : {request.table_name}")

    response_records: List[Dict[str, Any]] = []

    async with AsyncSessionLocal() as session:
        for record in request.records:
            sync_val = record.get("sync", 0)
            id_val = record.get("id", 0)

            # Cas spécial : table utilisateurs + nom_utilisateur == "admin"
            if request.table_name == "utilisateurs" and record.get("nom_utilisateur") == "admin":
                existing = await session.execute(
                    select(Utilisateur).where(Utilisateur.nom_utilisateur == "admin")
                )
                admin = existing.scalars().first()
                if admin is not None:
                    result_record = dict(record)
                    result_record["new_sync"] = admin.sync
                    response_records.append(result_record)
                    continue

            action = determine_action(sync_val, id_val)

            # Calculer max(sync) + 1
            max_sync_result = await session.execute(
                select(func.max(model.sync))
            )
            max_sync = max_sync_result.scalar() or 0
            new_sync = max_sync + 1

            # Construire les données à insérer
            insert_data = {k: v for k, v in record.items()}
            insert_data["action"] = action
            insert_data["sync"] = new_sync
            insert_data["id"] = id_val

            # Filtrer uniquement les colonnes du modèle et convertir les dates
            mapper = inspect(model).mapper
            valid_cols = {c.key for c in mapper.column_attrs}
            date_cols = {
                c.key
                for c in mapper.columns
                if isinstance(c.type, SADate)
            }
            insert_data = {k: v for k, v in insert_data.items() if k in valid_cols}
            for col in date_cols:
                val = insert_data.get(col)
                if isinstance(val, str) and val:
                    try:
                        insert_data[col] = datetime.fromisoformat(val).date()
                    except ValueError:
                        insert_data[col] = None
                elif not val:
                    insert_data[col] = None

            instance = model(**insert_data)
            session.add(instance)
            await session.flush()

            result_record = dict(record)
            result_record["new_sync"] = new_sync
            response_records.append(result_record)

        await session.commit()

    return response_records


@app.get("/get_interchange")
async def get_interchange(conteneur_uuid: str, sync: int, page: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
                select(Interchange).where(
                    Interchange.conteneur_uuid == conteneur_uuid,
                    Interchange.sync == sync,
                    Interchange.page == page,
                )
            )
        row = result.scalars().first()

    if row is None or row.scan is None:
        raise HTTPException(status_code=404, detail="Aucun enregistrement trouvé")

    nom_fichier = row.nom_fichier or "fichier"
    return Response(
        content=row.scan,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{nom_fichier}"'},
    )


@app.post("/post_interchange")
async def post_interchange(
    uuid: str = Form(...),
    id: int = Form(...),
    sync: int = Form(...),
    conteneur_uuid: str = Form(...),
    page: int = Form(...),
    nom_fichier: str = Form(...),
    scan: UploadFile = File(...),
):
    action = determine_action(sync, id)
    scan_bytes = await scan.read()

    async with AsyncSessionLocal() as session:
        max_sync_result = await session.execute(select(func.max(Interchange.sync)))
        max_sync = max_sync_result.scalar() or 0
        new_sync = max_sync + 1

        instance = Interchange(
            uuid=uuid,
            id=id,
            sync=new_sync,
            conteneur_uuid=conteneur_uuid,
            page=page,
            nom_fichier=nom_fichier,
            scan=scan_bytes,
            action=action,
        )
        session.add(instance)
        await session.commit()

    return {"new_sync": new_sync}
