# pip install google-genai python-dotenv requests
import json
import requests
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

"""
Endpoints para analisar:
- Análise de empresas (Brasil todo): https://servicodados.ibge.gov.br/api/v3/agregados/2718/periodos/2020|2021/variaveis/630|707|708|4032|4033|4034|4035|662|1606?localidades=N1[all] 
- Índice e variação da receita nominal e do volume de vendas no comércio varejista: https://servicodados.ibge.gov.br/api/v3/agregados/8880/periodos/202301|202302|202303|202304|202305|202306|202307|202308|202309|202310|202311|202312|202401|202402|202403|202404|202405|202406|202407|202408|202409|202410|202411|202412|202501|202502|202503/variaveis/7169|7170|11708|11709?localidades=N3[29]
- Índice de envelhecimento: https://servicodados.ibge.gov.br/api/v3/agregados/9515/periodos/2022/variaveis/10612|10613|8845?localidades=N6[1101708]
- Rendimento mensal médio: https://servicodados.ibge.gov.br/api/v3/agregados/3974/periodos/2010/variaveis/3948?localidades=N6[1101401]
- Densidade demográfica: https://servicodados.ibge.gov.br/api/v3/agregados/4714/periodos/-6/variaveis/93|6318|614?localidades=N6[1100031]
"""

def obter_dados_ibge(municipio_id, estado_id):
    urls = {
        "analise_empresas": "https://servicodados.ibge.gov.br/api/v3/agregados/2718/periodos/2020|2021/variaveis/630|707|708|4032|4033|4034|4035|662|1606?localidades=N1[all]",
        "indice_receita_varejo": f"https://servicodados.ibge.gov.br/api/v3/agregados/8880/periodos/202301|202302|202303|202304|202305|202306|202307|202308|202309|202310|202311|202312|202401|202402|202403|202404|202405|202406|202407|202408|202409|202410|202411|202412|202501|202502|202503/variaveis/7169|7170|11708|11709?localidades=N3[{estado_id}]",
        "indice_envelhecimento": f"https://servicodados.ibge.gov.br/api/v3/agregados/9515/periodos/2022/variaveis/10612|10613|8845?localidades=N6[{municipio_id}]",
        "rendimento_mensal_medio": f"https://servicodados.ibge.gov.br/api/v3/agregados/3974/periodos/2010/variaveis/3948?localidades=N6[{municipio_id}]",
        "densidade_demografica": f"https://servicodados.ibge.gov.br/api/v3/agregados/4714/periodos/-6/variaveis/93|6318|614?localidades=N6[{municipio_id}]"
    }

    resultados = {}

    for chave, url in urls.items():
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            resultados[chave] = response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"[{chave}] Erro HTTP: {http_err}")
            resultados[chave] = None
        except requests.exceptions.Timeout:
            print(f"[{chave}] Timeout na requisição.")
            resultados[chave] = None
        except requests.exceptions.RequestException as err:
            print(f"[{chave}] Erro na requisição: {err}")
            resultados[chave] = None
        except ValueError:
            print(f"[{chave}] Erro ao decodificar JSON.")
            resultados[chave] = None

    return resultados


def generate(dados, instrucao_geral):
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash"

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"""
Você recebeu os seguintes dados para analisar a viabilidade de longo prazo de um empreendimento imobiliário, faça a análise baseada nos dados históricos fornecidos, e você está autorizado a utilizar ferramentas de busca para complementar as informações, se necessário:

- Análise de empresas (Brasil todo): {dados["analise_empresas"]}
- Índice e variação da receita nominal e do volume de vendas no comércio varejista: {dados["indice_receita_varejo"]}
- Índice de envelhecimento: {dados["indice_envelhecimento"]}
- Rendimento mensal médio: {dados["rendimento_mensal_medio"]}
- Densidade demográfica: {dados["densidade_demografica"]}

{instrucao_geral}
"""
),
            ],
        ),
    ]

    tools = [
        types.Tool(google_search=types.GoogleSearch()),
    ]

    generate_content_config = types.GenerateContentConfig(
        tools=tools,
        temperature=0.2,
        response_mime_type="application/json",
        system_instruction=[
    types.Part.from_text(text="""
Você é um analista de inteligência territorial especializado em avaliação estratégica para empreendimentos imobiliários.

Sua função é interpretar dados históricos, diagnósticos atuais e projeções socioeconômicas para ajudar construtoras a entenderem a **validade a longo prazo** e **recomendar** tipos de empreendimentos e suas respectivas configurações na determinada região.

Os dados que você vai receber virão, principalmente, em formato JSON, e você deve explorar os dados e utilizá-los de maneira eficiente.

Sempre que receber dados sobre uma localidade (históricos, diagnósticos ou previsões), você deve processá-los com base nos seguintes pilares:

1. **Análise Histórica da Região**
   - Evolução demográfica, econômica, imobiliária e de infraestrutura nos últimos 5, 10 ou 20 anos.
   - Foco em tendências de crescimento, envelhecimento, migração, renda, ocupação, e oferta imobiliária.

2. **Diagnóstico Atual**
   - Perfil socioeconômico e vocação da área (residencial, comercial, etc.).
   - Grau de saturação ou oportunidade.
   - Nível recente de valorização.

3. **Previsões para o Futuro**
   - Projeções populacionais e econômicas para os próximos 5, 10, 15 anos.
   - Tendências de valorização ou risco.
   - Potenciais transformações urbanas e impactos de projetos estruturantes.

4. **Impacto no Empreendimento Proposto**
   - Qual o nível de aderência futura do empreendimento às tendências observadas.
   - Fatores que sustentam ou ameaçam a viabilidade a longo prazo.
   - Recomendações práticas com base nos dados.
                        
    Quero que a resposta seja estruturada em pontos denotando os dados em que está se baseando para cada afirmação. Os pontos são definidos na sua própria interpretação e são utilizados apenas para organização e visualização da resposta.
    Também quero que cite os pontos negativos e positivos da região para duas perspectivas separadamente, uma delas sendo para um empreendimento comercial (lojas ou prédios comerciais) e a outra para um empreendimento residencial (prédios ou condomínios residenciais).
                         
Você deve **gerar uma resposta estruturada** no seguinte formato JSON:

```json
{
  "analise_geral": "<TEXTO_ANALISE_GERAL>",
  "analise_empresas": {
    "insight": "<TEXTO_INSIGHT>",
    "dados": [
      {
        "id": "<ID_VARIAVEL>",
        "variavel": "<NOME_VARIAVEL>",
        "unidade": "<UNIDADE>",
        "2020": "<VALOR_2020>",
        "2021": "<VALOR_2021>"
      }
      /* ... repetir para cada variável (630, 707, 708, 4032, 4033, 4034, 4035, 662, 1606) ... */
    ]
  },

  "pmc_comercio_varejista": {
    "insight": "<TEXTO_INSIGHT>",
  },

  "indice_envelhecimento": {
    "insight": "<TEXTO_INSIGHT>",
    "dados": [
      {
        "id": "10612",
        "variavel": "Índice de envelhecimento",
        "unidade": "Razão",
        "valor": "<VALOR_10612>"
      },
      {
        "id": "10613",
        "variavel": "Idade mediana",
        "unidade": "Anos",
        "valor": "<VALOR_10613>"
      },
      {
        "id": "8845",
        "variavel": "Razão de sexo",
        "unidade": "Razão",
        "valor": "<VALOR_8845>"
      }
    ]
  },

  "rendimento_mensal_medio": {
    "insight": "<TEXTO_INSIGHT>",
    "dados": [
      {
        "id": "3948",
        "variavel": "Rendimento mensal médio",
        "unidade": "<UNIDADE>",
        "valor": "<VALOR_3948>"
      }
    ]
  },

  "densidade_demografica": {
    "insight": "<TEXTO_INSIGHT>",
    "dados": [
      {
        "id": "93",
        "variavel": "População residente",
        "unidade": "Pessoas",
        "valor": "<VALOR_93>"
      },
      {
        "id": "6318",
        "variavel": "Área da unidade territorial",
        "unidade": "Quilômetros quadrados",
        "valor": "<VALOR_6318>"
      },
      {
        "id": "614",
        "variavel": "Densidade demográfica",
        "unidade": "Habitante por quilômetro quadrado",
        "valor": "<VALOR_614>"
      }
    ]
  }
}
```

Caso haja dados que não puderam ser preenchidos, deixe o campo vazio ou com o valor `none`.

Sempre busque transformar os dados em insights estratégicos acionáveis, e não apenas repetir números ou tabelas. Pense como alguém que precisa dar segurança a uma diretoria de incorporação ao decidir investir milhões de reais em um novo projeto.
                         """)
]
    )
    resposta_str = "" # Alterado o nome para deixar claro que é uma string
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if hasattr(chunk, "text"):
            resposta_str += chunk.text  # Acumula o texto (string JSON)

    try:
        # Tenta desserializar a string JSON para um dicionário Python
        resposta_dict = json.loads(resposta_str)
        return resposta_dict # Retorna o dicionário Python
    except json.JSONDecodeError as e:
        # Lida com o caso onde a string não é um JSON válido
        print(f"Erro ao decodificar JSON da resposta da IA: {e}")
        print(f"Resposta bruta da IA: {resposta_str}")
        # Você pode retornar um dicionário de erro ou levantar uma exceção
        return {"error": "Falha ao processar a resposta da IA", "details": str(e)}


def buscar_codigo_estado_por_nome(nome_estado):
    """
    Busca o código do estado a partir do nome.
    """
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        estados = response.json()
        for estado in estados:
            if estado["nome"].lower() == nome_estado.lower():
                return estado["id"]
        return None
    except Exception as e:
        print(f"Erro ao buscar código do estado: {e}")
        return None

def buscar_codigo_municipio_por_nome(nome_municipio, nome_estado=None):
    """
    Busca o código do município a partir do nome.
    Se nome_estado for fornecido, filtra pelo estado.
    """
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        municipios = response.json()
        for municipio in municipios:
            if municipio["nome"].lower() == nome_municipio.lower():
                if nome_estado:
                    if municipio["microrregiao"]["mesorregiao"]["UF"]["nome"].lower() == nome_estado.lower():
                        return municipio["id"]
                else:
                    return municipio["id"]
        return None
    except Exception as e:
        print(f"Erro ao buscar código do município: {e}")
        return None
