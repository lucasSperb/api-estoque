import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Documento

COLECOES = {"produtos", "clientes", "vendas", "movs"}
ID_MAX = 64


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Cria a tabela na primeira execução. Para evoluir o esquema depois, use Alembic.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Controle de Estoque e Vendas API", version="1.0.0", lifespan=lifespan)

# ALLOWED_ORIGINS: domínios do front separados por vírgula. Sem a variável, libera tudo (só para testes).
_origens = [o.strip().rstrip("/") for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origens,
    allow_methods=["GET", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


def _colecao(nome: str) -> str:
    if nome not in COLECOES:
        raise HTTPException(status_code=404, detail="Coleção desconhecida.")
    return nome


@app.get("/")
def raiz():
    return {"servico": "controle-estoque-vendas", "status": "ok", "docs": "/docs"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "banco": "ok"}


@app.get("/{colecao}")
def listar(colecao: str, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    _colecao(colecao)
    linhas = db.scalars(
        select(Documento).where(Documento.colecao == colecao).order_by(Documento.criado_em, Documento.id)
    ).all()
    return [l.dados for l in linhas]


@app.put("/{colecao}/{item_id}")
def salvar(colecao: str, item_id: str, dados: dict[str, Any], db: Session = Depends(get_db)) -> dict[str, Any]:
    _colecao(colecao)
    if not item_id or len(item_id) > ID_MAX:
        raise HTTPException(status_code=422, detail="Identificador inválido.")
    if "id" in dados and dados["id"] != item_id:
        raise HTTPException(status_code=422, detail="O id do corpo difere do id da rota.")
    dados["id"] = item_id

    linha = db.get(Documento, (colecao, item_id))
    if linha is None:
        db.add(Documento(colecao=colecao, id=item_id, dados=dados))
    else:
        linha.dados = dados
    db.commit()
    return dados


@app.delete("/{colecao}/{item_id}", status_code=204)
def remover(colecao: str, item_id: str, db: Session = Depends(get_db)) -> Response:
    _colecao(colecao)
    db.execute(delete(Documento).where(Documento.colecao == colecao, Documento.id == item_id))
    db.commit()
    return Response(status_code=204)
