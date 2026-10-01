import os
import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

async def init_db():
    if DATABASE_URL:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS cargos (
                id SERIAL PRIMARY KEY,
                from_location TEXT,
                to_location TEXT,
                date TEXT,
                body_type TEXT,
                weight_t FLOAT,
                volume_m3 FLOAT,
                price_usd FLOAT,
                cargo TEXT,
                company TEXT,
                telegram TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await conn.close()

@app.on_event("startup")
async def startup():
    await init_db()

class Cargo(BaseModel):
    from_loc: Optional[str] = Field(None, alias="from")
    to_loc: Optional[str] = Field(None, alias="to")
    origin: Optional[str] = None
    destination: Optional[str] = None
    date: Optional[str] = ""
    bodyType: Optional[str] = None
    body_type: Optional[str] = None
    weightT: Optional[float] = 0.0
    weight_tons: Optional[float] = 0.0
    volumeM3: Optional[float] = 0.0
    priceUsd: Optional[float] = 0.0
    price: Optional[float] = 0.0
    cargo: Optional[str] = ""
    company: Optional[str] = ""
    telegram: Optional[str] = ""
    phone: Optional[str] = ""

@app.get("/api/cargos")
async def get_cargos():
    if not DATABASE_URL:
        return []
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT * FROM cargos ORDER BY id DESC")
    await conn.close()
    
    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "from": r["from_location"] or "",
            "to": r["to_location"] or "",
            "date": r["date"] or "",
            "bodyType": r["body_type"] or "",
            "weightT": r["weight_t"] or 0,
            "volumeM3": r["volume_m3"] or 0,
            "priceUsd": r["price_usd"] or 0,
            "cargo": r["cargo"] or "",
            "company": r["company"] or "",
            "telegram": r["telegram"] or ""
        })
    return result

@app.post("/api/cargos")
async def add_cargo(cargo: Cargo):
    if not DATABASE_URL:
        return {"status": "error", "message": "База данных не подключена"}
        
    f_loc = cargo.from_loc or cargo.origin or ""
    t_loc = cargo.to_loc or cargo.destination or ""
    b_type = cargo.bodyType or cargo.body_type or ""
    w_t = cargo.weightT or cargo.weight_tons or 0.0
    p_usd = cargo.priceUsd or cargo.price or 0.0
    tg = cargo.telegram or cargo.phone or ""

    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        '''INSERT INTO cargos(from_location, to_location, date, body_type, weight_t, volume_m3, price_usd, cargo, company, telegram) 
           VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)''',
        f_loc, t_loc, cargo.date or "", b_type, float(w_t), float(cargo.volumeM3 or 0), float(p_usd), cargo.cargo or "", cargo.company or "", tg
    )
    await conn.close()
    return {"status": "ok", "message": "Груз успешно опубликован"}
