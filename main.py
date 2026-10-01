import os
import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aiogram import Bot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN) if BOT_TOKEN else None

class Cargo(BaseModel):
    origin: str
    destination: str
    body_type: str
    weight_tons: float
    price: float
    phone: str

@app.post("/api/cargos")
async def add_cargo(cargo: Cargo):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        '''INSERT INTO cargos(origin, destination, body_type, weight_tons, price, phone) 
           VALUES($1, $2, $3, $4, $5, $6)''',
        cargo.origin, cargo.destination, cargo.body_type, cargo.weight_tons, cargo.price, cargo.phone
    )
    await conn.close()
    return {"status": "ok", "message": "Груз успешно опубликован"}
