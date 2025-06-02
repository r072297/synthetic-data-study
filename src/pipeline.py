from src.infra import Logger
from src.infra import CONFIG
from .gerador import gerar_dados_sinteticos
from .analisador import aplicar_prefix_span, encontrar_sequencias_curtas


def run_pipeline(runs: int):
    for run in range(runs):
        CONFIG.data_dir=f"data/pipeline/run_{run+1}/"
        CONFIG.logs_path = f"./data/pipeline/run_{run+1}/run_{run+1}.log"
        CONFIG.spmf_input_file_path = f"pipe_input_{run+1}"
        CONFIG.spmf_output_file_path = f"pipe_output_{run+1}"
        logger = Logger()
        gerar_dados_sinteticos(logger)
        aplicar_prefix_span(logger)
        encontrar_sequencias_curtas(logger)
        logger.reset_instance()
