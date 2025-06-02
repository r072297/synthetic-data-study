import os, subprocess, re
from collections import Counter
from src.infra import chamar_prefix_span, Logger, CONFIG

def aplicar_prefix_span(logger: Logger):
    chamar_prefix_span(logger)

def encontrar_sequencias_curtas(logger: Logger):
    sequencias_corrupcao = Counter()
    sequencias_corrupcao['curta'] = 0
    sequencias_corrupcao['longa'] = 0

    output_path = os.path.join(CONFIG.data_dir, f"{CONFIG.spmf_output_file_path}.txt")

    try:
        result = subprocess.run(
            ['grep', '-i', 'concessao sim | revisao nao | #SUP', output_path],
            capture_output=True, text=True, check=False
        )
        match = re.search(r'(\d+)$', result.stdout)
        if match:
            sequencias_corrupcao['curta'] = int(match.group(1))
            logger.log_info(f"Sequências corrupção curta: {sequencias_corrupcao['curta']}")
        else:
            sequencias_corrupcao['curta'] = 0
            logger.log_info("Nenhuma sequência corrupção curta encontrada")
    except Exception as e:
        logger.log_error(f"Erro ao executar grep: {e}")

    try:
        result = subprocess.run(
            ['grep', '-i', 'concessao sim | revisao sim | pagamento nao | #SUP', output_path],
            capture_output=True, text=True, check=False
        )
        match = re.search(r'(\d+)$', result.stdout)
        if match:
            sequencias_corrupcao['longa'] = int(match.group(1))
            logger.log_info(f"Sequências corrupção longa: {sequencias_corrupcao['longa']}")
        else:
            sequencias_corrupcao['longa'] = 0
            logger.log_info("Nenhuma sequência corrupção longa encontrada")
    except Exception as e:
        logger.log_error(f"Erro ao executar grep: {e}")


    return sequencias_corrupcao
