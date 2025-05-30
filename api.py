from fastapi import FastAPI, Query
from typing import List, Optional

from ia import obter_dados_ibge, generate, buscar_codigo_estado_por_nome, buscar_codigo_municipio_por_nome

app = FastAPI()

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
    return generate(dados, instrucao_geral="Gerar relatório comercial com as seguintes especificações")

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
    cod_municipio = buscar_codigo_municipio_por_nome(estado)
    dados = obter_dados_ibge(cod_estado, cod_municipio)
    return generate(dados, instrucao_geral="Gerar relatório para empreendimento residencial com as seguintes especificações")

