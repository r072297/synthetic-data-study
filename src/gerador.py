from typing import Dict, List, Tuple
from src.infra import Logger, CONFIG, save_as_json, save_as_txt
from src.servicos import Servidor, Cidadao, Evento, run_simulation
from dataclasses import asdict
from src.servicos import input_para_prefix_span

def gerar_dados_sinteticos(logger: Logger) -> Tuple[List[Evento], Dict[int, Cidadao], Dict[int,Servidor]]:
    eventos, cidadaos, servidores, eventos_corruptos = run_simulation(logger)
    save_as_json(logger, "cidadaos", [asdict(cidadao) for _, cidadao in cidadaos.items()], CONFIG.data_dir)
    save_as_json(logger, "servidores", [asdict(servidor) for _,servidor in servidores.items()], CONFIG.data_dir)
    save_as_json(logger, "eventos", [asdict(evento) for evento in eventos], CONFIG.data_dir)
    save_as_json(logger, "eventos_corruptos", eventos_corruptos, CONFIG.data_dir)
    logger.log_info(f"Dados da simulação salvos (diretório base: {CONFIG.data_dir})")
    # preprocessmento para prefix span
    input = input_para_prefix_span(logger, eventos)
    save_as_txt(logger, CONFIG.spmf_input_file_path,input,CONFIG.data_dir)
    return eventos, cidadaos, servidores
