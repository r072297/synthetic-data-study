from dataclasses import dataclass, field
from typing import List

@dataclass
class Requisitos:
    concessao: List[str] = field(default_factory=list)
    revisao: List[str] = field(default_factory=list)
    pagamento: List[str] = field(default_factory=list)

@dataclass
class ProgramaSocial:
    nome: str
    orgao: str
    requisitos: Requisitos

auxilio_alimentacao = ProgramaSocial(
    "Auxílio Alimentação",
    "Secretaria de Assistência Social",
    Requisitos(
        concessao=["baixa_renda"],
        revisao=["baixa_renda"],
        pagamento=["baixa_renda"]
    )
)

bolsa_estudantil = ProgramaSocial(
    "Bolsa Estudantil",
    "Secretaria de Educação",
    Requisitos(
        concessao=["idade", "baixa_renda", "matricula"],
        revisao=["idade", "baixa_renda", "matricula"],
        pagamento=["idade", "baixa_renda", "matricula","frequencia_escolar"]
    )
)

auxilio_transporte = ProgramaSocial(
    "Auxílio Transporte",
    "Secretaria de Mobilidade Urbana",
    Requisitos(
        concessao=["baixa_renda", "condicao_especial"],
        revisao=["baixa_renda", "condicao_especial"],
        pagamento=["baixa_renda", "condicao_especial", "uso_transporte"]
    )
)

vale_gas = ProgramaSocial(
    "Vale Gás",
    "Secretaria de Assistência Social",
    Requisitos(
        concessao=["baixa_renda", "composicao_familiar"],
        revisao=["baixa_renda", "composicao_familiar"],
        pagamento=["baixa_renda", "composicao_familiar"]
    )
)

auxilio_creche = ProgramaSocial(
    "Auxílio Creche",
    "Secretaria de Educação",
    Requisitos(
        concessao=["idade", "baixa_renda", "filhos_menores"],
        revisao=["idade","baixa_renda", "filhos_menores"],
        pagamento=["idade","baixa_renda", "filhos_menores","frequencia_creche"]
    )
)

@dataclass
class UnidadeGestora:
    nome: str
    conformidade: float
    qtd_servidores: int
    programas_geridos: List[str]

ug_assistencia = UnidadeGestora("UG Assistência Social", 0.5, 3, ["Auxílio Alimentação"])

ug_educacao = UnidadeGestora("UG Educação", 0.8, 3, ["Bolsa Estudantil", "Auxílio Creche"])

ug_mobilidade = UnidadeGestora("UG Mobilidade Urbana", 0.4, 3, ["Auxílio Transporte"])

ug_multipla = UnidadeGestora("UG Assistência Múltipla", 0.6, 3, ["Auxílio Alimentação", "Vale Gás"])

ug_central = UnidadeGestora("UG Central", 0.9, 3, ["Auxílio Alimentação", "Bolsa Estudantil", "Auxílio Transporte"])

@dataclass
class Config:
    # pipeline
    pipe_runs_padrao: int
    # simulacao
    sim_total_cidadaos: int
    sim_eventos: List[str]
    sim_orgaos: List[str]
    sim_programas_sociais: List[ProgramaSocial]
    sim_unidades_gestoras: List[UnidadeGestora]
    # geracao
    sim_corruptibilidade_limiar: float
    sim_corruptibilidade_cidadaos_mu: float
    sim_corruptibilidade_cidadaos_sigma: float
    sim_corruptibilidade_servidores_mu: float
    sim_corruptibilidade_servidores_sigma: float
    sim_eventos_duracao_mu: float
    sim_eventos_duracao_sigma: float
    # analise
    spmf_timeout: int
    spmf_prefix_span_min_support: float
    spmf_output_file_path: str
    spmf_input_file_path: str
    spmf_prefix_span_pattern_max_lenght: int
    # outros
    data_dir: str
    logs_console: bool
    logs_path: str
    logs_level: str

# Instanciamento único
CONFIG = Config(
    pipe_runs_padrao=5,
    sim_total_cidadaos=10000,
    sim_eventos=["concessao", "revisao", "pagamento"],
    sim_eventos_duracao_mu = 20,
    sim_eventos_duracao_sigma = 5,
    sim_orgaos=["Secretaria de Assistência Social", "Secretaria de Habitação"],
    sim_programas_sociais=[
        auxilio_alimentacao,
        auxilio_creche,
        bolsa_estudantil
        # auxilio_transporte,
        # vale_gas,
        ],
    sim_unidades_gestoras=[ug_assistencia,ug_educacao],
    sim_corruptibilidade_limiar = 0.6,
    sim_corruptibilidade_cidadaos_mu = 0.4,
    sim_corruptibilidade_cidadaos_sigma = 0.3,
    sim_corruptibilidade_servidores_mu = 0.2,
    sim_corruptibilidade_servidores_sigma = 0.15,
    spmf_timeout=30000,
    spmf_prefix_span_min_support= 0.001,
    spmf_input_file_path= "spmf_input",
    spmf_output_file_path= "spmf_output",
    spmf_prefix_span_pattern_max_lenght= 20,
    data_dir="data/simulados/",
    logs_console=True,
    logs_path="data/simulador.log",
    logs_level="DEBUG"
)
