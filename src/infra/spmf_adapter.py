import subprocess
from typing import Tuple
from .logger import Logger
from .config import CONFIG

def chamar_prefix_span(logger: Logger) -> Tuple[bool, str, str]:
    logger.log_info(f"Início PrefixSpan no SPMF com timeout de {CONFIG.spmf_timeout}")
    path_input = "./" + CONFIG.data_dir + CONFIG.spmf_input_file_path+".txt"
    path_output = "./" + CONFIG.data_dir + CONFIG.spmf_output_file_path+".txt"
    min_support = CONFIG.spmf_prefix_span_min_support
    command = [
        "spmf",
        "run",
        "PrefixSpan",
        path_input,
        path_output,
        str(min_support)+"%",
        str(CONFIG.spmf_prefix_span_pattern_max_lenght)
    ]
    try:
        resultado = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=CONFIG.spmf_timeout,
            check=False
        )

        sucesso = resultado.returncode == 0
        stdout = resultado.stdout or ""
        stderr = resultado.stderr or ""

        if sucesso:
            logger.log_info("SPMF PrefixSpan executado com sucesso")
        else:
            logger.log_error(f"SPMF PrefixSpan falhou com código {resultado.returncode}")
            logger.log_error(f"Stderr: {stderr}")

        return sucesso, stdout, stderr

    except subprocess.TimeoutExpired:
        logger.log_error(f"Comando SPMF excedeu timeout de {CONFIG.spmf_timeout}s")
        return False, "", "Timeout excedido"
    except FileNotFoundError:
        logger.log_error("Java ou SPMF não encontrado no sistema")
        return False, "", "Java ou SPMF não encontrado"
    except Exception as e:
        logger.log_error(f"Erro inesperado ao executar comando SPMF: {e}")
        return False, "", str(e)
