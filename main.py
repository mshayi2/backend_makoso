import uuid as uuid_lib
from contextlib import asynccontextmanager
from typing import Dict, List, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, inspect, func

from database import engine, Base, AsyncSessionLocal
from models import (
    Monnaie, Utilisateur, Client, Dossier, Conteneur, DetailConteneur,
    Interchange, DepotArgent, Depense, Camion, ChauffeurConvoyeur, Voyage
)

TABLE_MAP = {
    "utilisateurs": Utilisateur,
    "monnaies": Monnaie,
    "clients": Client,
    "dossiers": Dossier,
    "conteneurs": Conteneur,
    "detail_conteneurs": DetailConteneur,
    "interchange": Interchange,
    "depot_argent": DepotArgent,
    "depenses": Depense,
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

            # Filtrer uniquement les colonnes du modèle
            valid_cols = {c.key for c in inspect(model).mapper.column_attrs}
            insert_data = {k: v for k, v in insert_data.items() if k in valid_cols}

            instance = model(**insert_data)
            session.add(instance)
            await session.flush()

            result_record = dict(record)
            result_record["new_sync"] = new_sync
            response_records.append(result_record)

        await session.commit()

    return response_records
