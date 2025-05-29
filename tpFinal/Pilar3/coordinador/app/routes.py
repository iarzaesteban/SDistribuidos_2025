import redis
import json
import hashlib
import time
import uuid
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from utils.logger import logger
from datetime import datetime


router = APIRouter()
r = redis.Redis(host='redis', port=6379, decode_responses=True)
class Transaction(BaseModel):
    id: int
    amount: float
    description: str

@router.get("/")
def root():
    return {"mensaje": f"Hola bebeee"}

def generar_hash_dummy():
    return hashlib.sha256(str(datetime.now()).encode()).hexdigest()


@router.post("/nombre")
async def guardar_nombre(nombre: str):
    r.rpush("nombres", nombre)
    return {"mensaje": "Nombre guardado en Redis con éxito"}

@router.get("/nombres")
async def obtener_nombres():
    nombres = r.lrange("nombres", 0, -1)
    return {"nombres": nombres}