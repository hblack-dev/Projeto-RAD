from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import requests
from datetime import datetime, timedelta
import logging
from apscheduler.schedulers.background import BackgroundScheduler


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
    dataAtualizacao = Column(String)

Base.metadata.create_all(bind=engine)



app = FastAPI()


def atualizar_empresa(cnpj: str):
    db = SessionLocal()

    try:
        try:
            r = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")
            r.raise_for_status()
            dados = r.json()
        except:
            logging.error(f"Erro ao buscar CNPJ {cnpj}")
            return {"erro": "API falhou"}
        
        empresa = db.query(Empresa).filter(Empresa.cnpj == cnpj).first()

        if empresa:
            empresa.nome = dados.get("razao_social")
            empresa.cidade = dados.get("municipio")
            empresa.estado = dados.get("uf")
            empresa.situacao = dados.get("situacao")  # 👈 NOVO
            empresa.data_atualizacao = datetime.now().isoformat()

            db.commit()
            logging.info(f"Empresa {cnpj} atualizada")

            return {"msg": "empresa atualizada"}
        
        else:
            nova = Empresa(
                cnpj = cnpj,
                nome = dados.get("razao_social"),
                cidade = dados.get("municipio"),
                estado = dados.get("uf"),
                situacao = dados.get("situacao"),
                data_atualizacao = datetime.now().isoformat()
            )

            db.add(nova)
            db.commit()
            logging.info(f"Empresa {cnpj} criada")

            return {"msg": "empresa criada"}
        
    finally:
        db.close()


def empresasDesatualizadas(): 
    db = SessionLocal()

    try: 
        limite = datetime.now() - timedelta(days = 30)
        empresas = db.query(Empresa).all()

        return [
            e.cnpj for e in empresas
            if datetime.fromisoformat(e.data_atualizacao) < limite
        ]
    
    finally:
        db.close()

