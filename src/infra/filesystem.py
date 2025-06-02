import os
import json
from typing import Any
from src.infra.logger import Logger
from typing import List

def create_directory(logger: Logger, path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)
        logger.log_info(f"Diretório criado (ou já existente): {path}")
    except Exception as e:
        logger.log_error(f"Erro ao criar diretório {path}: {e}")
        raise

def save_as_json(logger: Logger, filename: str, content: Any, save_dir_path:str) -> str:
    if not os.path.exists(save_dir_path):
        os.makedirs(save_dir_path, exist_ok=True)
    file_path = os.path.join(save_dir_path, f"{filename}.json")
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        logger.log_info(f"Arquivo JSON '{filename}.json' salvo em {file_path}")
        return file_path
    except Exception as e:
        logger.log_error(f"Erro ao salvar arquivo JSON {file_path}: {e}")
        raise

def save_as_txt(logger: Logger, filename: str, content: List[List[int]], save_dir_path:str) -> str:
    if not os.path.exists(save_dir_path):
        os.makedirs(save_dir_path, exist_ok=True)
    file_path = os.path.join(save_dir_path, f"{filename}.txt")
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding='utf-8') as f:
            for lista in content:
                linha = ' '.join(map(str, lista))
                f.write(linha + '\n')
        logger.log_info(f"Arquivo TXT '{filename}.txt' salvo em {file_path}")
        return file_path
    except Exception as e:
        logger.log_error(f"Erro ao salvar arquivo TXT {file_path}: {e}")
        raise

def read_txt(logger: Logger, filename: str, save_dir_path:str) -> List[List[str]]:
    file_path = os.path.join(save_dir_path, f"{filename}.txt")
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            content = [list(f)]
        logger.log_info(f"Arquivo TXT '{filename}.txt' lido de {file_path}")
        return content
    except Exception as e:
        logger.log_error(f"Erro ao ler arquivo TXT {file_path}: {e}")
        raise
