from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import requests
from datetime import datetime, timedelta
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import atexit


logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


databaseUrl = "postgresql://postgres:1234@localhost:5432/empresas"

engine = create_engine(databaseUrl)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True)
    cnpj = Column(String, unique=True)
    nome = Column(String)
    cidade = Column(String)
    estado = Column(String)
    situacao = Column(String)
    data_atualizacao = Column(DateTime)

Base.metadata.create_all(bind=engine)


app = FastAPI()


def cnpj_valido(cnpj: str):
    return cnpj.isdigit() and len(cnpj) == 14


def buscar_cnpj_api(cnpj: str):
    try:
        resposta = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")
        resposta.raise_for_status()
        return resposta.json()
    except Exception as e:
        logging.error(f"Erro ao buscar CNPJ {cnpj}: {e}")
        return None


@app.get("/empresa/{cnpj}")
def buscar_empresa(cnpj: str):
    if not cnpj_valido(cnpj):
        raise HTTPException(status_code=400, detail="CNPJ inválido, informe 14 dígitos numéricos")

    db = SessionLocal()

    empresa = db.query(Empresa).filter(Empresa.cnpj == cnpj).first()

    if empresa:
        db.close()
        return {
            "cnpj": empresa.cnpj,
            "nome": empresa.nome,
            "cidade": empresa.cidade,
            "situacao": empresa.situacao
        }

    dados = buscar_cnpj_api(cnpj)

    if not dados:
        db.close()
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    nova_empresa = Empresa(
        cnpj=cnpj,
        nome=dados.get("razao_social"),
        cidade=dados.get("municipio"),
        estado=dados.get("uf"),
        situacao=dados.get("descricao_situacao_cadastral"),
        data_atualizacao=datetime.now()
    )

    db.add(nova_empresa)
    db.commit()
    db.close()

    logging.info(f"Empresa {cnpj} salva")

    return {
        "cnpj": nova_empresa.cnpj,
        "nome": nova_empresa.nome,
        "cidade": nova_empresa.cidade,
        "situacao": nova_empresa.situacao
    }


@app.post("/empresa/{cnpj}")
def criar_atualizar_empresa(cnpj: str):
    if not cnpj_valido(cnpj):
        raise HTTPException(status_code=400, detail="CNPJ inválido, informe 14 dígitos numéricos")

    db = SessionLocal()

    dados = buscar_cnpj_api(cnpj)

    if not dados:
        db.close()
        raise HTTPException(status_code=404, detail="Erro ao buscar empresa na API")

    empresa = db.query(Empresa).filter(Empresa.cnpj == cnpj).first()

    if empresa:
        empresa.nome = dados.get("razao_social")
        empresa.cidade = dados.get("municipio")
        empresa.estado = dados.get("uf")
        empresa.situacao = dados.get("descricao_situacao_cadastral")
        empresa.data_atualizacao = datetime.now()

        db.commit()
        db.close()

        logging.info(f"Empresa {cnpj} atualizada")
        return {"msg": "empresa atualizada"}

    nova_empresa = Empresa(
        cnpj=cnpj,
        nome=dados.get("razao_social"),
        cidade=dados.get("municipio"),
        estado=dados.get("uf"),
        situacao=dados.get("descricao_situacao_cadastral"),
        data_atualizacao=datetime.now()
    )

    db.add(nova_empresa)
    db.commit()
    db.close()

    logging.info(f"Empresa {cnpj} criada")
    return {"msg": "empresa criada"}


@app.get("/empresas")
def listar_empresas():
    db = SessionLocal()
    empresas = db.query(Empresa).all()
    db.close()

    lista = []
    for e in empresas:
        lista.append({
            "cnpj": e.cnpj,
            "nome": e.nome,
            "cidade": e.cidade,
            "situacao": e.situacao
        })

    return lista


@app.delete("/empresa/{cnpj}")
def deletar_empresa(cnpj: str):
    db = SessionLocal()

    empresa = db.query(Empresa).filter(Empresa.cnpj == cnpj).first()

    if not empresa:
        db.close()
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    db.delete(empresa)
    db.commit()
    db.close()

    logging.info(f"Empresa {cnpj} deletada")
    return {"msg": "Empresa deletada com sucesso"}


def atualizar_empresas_antigas():
    db = SessionLocal()

    trinta_dias_atras = datetime.now() - timedelta(days=30)
    empresas = db.query(Empresa).all()

    for empresa in empresas:
        if empresa.data_atualizacao and empresa.data_atualizacao < trinta_dias_atras:
            dados = buscar_cnpj_api(empresa.cnpj)

            if dados:
                empresa.nome = dados.get("razao_social")
                empresa.cidade = dados.get("municipio")
                empresa.estado = dados.get("uf")
                empresa.situacao = dados.get("descricao_situacao_cadastral")
                empresa.data_atualizacao = datetime.now()

                logging.info(f"Empresa {empresa.cnpj} atualizada")

    db.commit()
    db.close()

    logging.info("Atualização mensal concluída")


scheduler = BackgroundScheduler()
scheduler.add_job(atualizar_empresas_antigas, "interval", days=30)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())