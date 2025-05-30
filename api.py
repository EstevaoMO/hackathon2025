from fastapi import FastAPI, Query
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

from ia import obter_dados_ibge, generate, buscar_codigo_estado_por_nome, buscar_codigo_municipio_por_nome

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para desenvolvimento, permite qualquer origem
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return "Olá, bem-vindo à API do GeoInsights"

@app.get("/relatorio/comercial")
def relatorio_comercial(
    estado: str = Query(..., alias="localizacao.estado"),
    municipio: str = Query(..., alias="localizacao.municipio"),
    numero_unidades_salas: str = Query(...),
    tamanho_medio_por_unidade_m2: str = Query(...),
    uso_principal: str = Query(...),
    faixa_preco_min: str = Query(..., alias="faixa_preco_estimado.min"),
    faixa_preco_max: str = Query(..., alias="faixa_preco_estimado.max"),
    presenca_estacionamento: str = Query(...),
    infraestrutura: Optional[List[str]] = Query(None)
):
    
    cod_estado = buscar_codigo_estado_por_nome(estado)
    cod_municipio = buscar_codigo_municipio_por_nome(municipio, estado)
    dados = obter_dados_ibge(cod_estado, cod_municipio)
    return generate(dados, instrucao_geral=f"Ao gerar relatório comercial, leve em conta as seguintes especificações: numero_unidades_salas:{numero_unidades_salas} tamanho_medio_por_unidade_m2: {tamanho_medio_por_unidade_m2} uso_principal:{uso_principal} faixa_preco_min:{faixa_preco_min} faixa_preco_max:{faixa_preco_max} presenca_estacionamento:{presenca_estacionamento} infraestrutura:{infraestrutura}")

@app.get("/relatorio/residencial")
def relatorio_residencial(
    estado: str = Query(..., alias="localizacao.estado"),
    municipio: str = Query(..., alias="localizacao.municipio"),
    numero_unidades: str = Query(...),
    tamanho_medio_por_unidade_m2: str = Query(...),
    numero_dormitorios: str = Query(...),
    faixa_preco_min: str = Query(..., alias="faixa_preco_estimado.min"),
    faixa_preco_max: str = Query(..., alias="faixa_preco_estimado.max"),
    presenca_area_comum: str = Query(...),
    itens_area_comum: Optional[List[str]] = Query(None)
):
    cod_estado = buscar_codigo_estado_por_nome(estado)
    cod_municipio = buscar_codigo_municipio_por_nome(municipio, estado)
    dados = obter_dados_ibge(municipio_id=cod_municipio, estado_id=cod_estado)
    return generate(dados, instrucao_geral=f"Ao gerar relatório residencial, leve em conta as seguintes especificações: numero_unidades:{numero_unidades} tamanho_medio_por_unidade_m2:{tamanho_medio_por_unidade_m2} numero_dormitorios:{numero_dormitorios} faixa_preco_min:{faixa_preco_min} faixa_preco_max:{faixa_preco_max} presenca_area_comum:{presenca_area_comum} itens_area_comum:{itens_area_comum}")