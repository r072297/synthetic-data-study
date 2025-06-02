from collections import defaultdict
from dataclasses import asdict
from .simulacao import Evento
from typing import List, Dict, Tuple
from src.infra import Logger
import re
import unicodedata

def arrays_item_sets(eventos: List[Evento])->Dict[int, List[List[str]]]:
    sequencias_cidadaos = defaultdict(list)
    items_de_interesse_evento = ["evento","mantido"]
    for evento in eventos:
        valores_interesse = \
        [asdict(evento)[key] for key in items_de_interesse_evento]
        sequencias_cidadaos\
            [f"{evento.cidadao_id}|{evento.nome_programa}"]\
            .append(list(valores_interesse))
    return sequencias_cidadaos

def tradutor_item(lista, item):
    try:
        return lista.index(item) + 1
    except ValueError:
        lista.append(item)
        return len(lista)

def traduzir_estrutura_item_set(sequencias_cidadaos: Dict[int, List[List[str]]]) -> Tuple[Dict[int, List[List[int]]], List[str]]:
    traducoes = defaultdict(list)
    dicionario = []
    for cidadao_id, sequencias in sequencias_cidadaos.items():
        for sequencia in sequencias:
            sequencia_traduzida = []
            for item in sequencia:
                sequencia_traduzida.append(tradutor_item(dicionario, item))
            traducoes[cidadao_id].append(sequencia_traduzida)
    return traducoes , dicionario

def estrutura_item_set_traduzida(logger:Logger, eventos: List[Evento]) -> Tuple[Dict[int, List[List[int]]], List[str]]:
    sequencias_item_sets = arrays_item_sets(eventos)
    traducoes , dicionario= traduzir_estrutura_item_set(sequencias_item_sets)
    return traducoes, dicionario

def sequencias_para_prefix_span(logger, eventos: List[Evento])-> Tuple[List[int],List[str]]:
    estrutura,dicionario = estrutura_item_set_traduzida(logger, eventos)
    sequencias_prefix_span = []
    for i, sequence in estrutura.items():
        sequence_flattened = []
        for item_set in sequence:
            for item in item_set:
                sequence_flattened.append(item)
            sequence_flattened.append(-1)
        sequence_flattened.append(-2)
        sequencias_prefix_span.append(sequence_flattened)
    return sequencias_prefix_span, dicionario

def convercao_snake_case(logger, texto):
    texto_sem_acento = unicodedata.normalize('NFD', texto)
    texto_sem_acento = ''.join(c for c in texto_sem_acento if unicodedata.category(c) != 'Mn')
    texto_normalizado = texto_sem_acento.lower()
    texto_limpo = re.sub(r'[^a-z0-9\s]', '', texto_normalizado)
    texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()
    snake_case = texto_limpo.replace(' ', '_')
    snake_case = re.sub(r'_+', '_', snake_case)
    snake_case = snake_case.strip('_')
    return snake_case


def gerar_cabecalho_prefixspan(logger, dicionario)-> List[List[str]]:
    linhas = [["@CONVERTED_FROM_TEXT"]]
    for indice, nome_item in enumerate(dicionario):
        numero_item = indice + 1
        nome_snake_case = convercao_snake_case(logger,nome_item)
        linhas.append([f"@ITEM={numero_item}={nome_snake_case}"])
    linhas.append(["@ITEM=-1=|"])
    return linhas

def input_para_prefix_span(logger: Logger, eventos: List[Evento])-> List:
    sequencias, dicionario = sequencias_para_prefix_span(logger, eventos)
    header = gerar_cabecalho_prefixspan(logger, dicionario)
    return header + sequencias
