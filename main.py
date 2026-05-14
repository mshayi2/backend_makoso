import uuid as uuid_lib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select

from database import engine, Base, AsyncSessionLocal
from models import Monnaie


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
