import itertools, math, random, simpy
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple, Optional, Generator
from ..infra import CONFIG, Logger, ProgramaSocial, UnidadeGestora
from collections import Counter

@dataclass
class Cidadao:
    id: int
    corruptibilidade: float
    atributos_sociais: List[str]

@dataclass
class EscolhaProgramaUnidade:
    programa: ProgramaSocial
    unidade_gestora: UnidadeGestora

@dataclass
class Servidor:
    unidade_gestora: UnidadeGestora
    id: int
    corruptibilidade: float

@dataclass
class Evento:
    nome_programa: str
    cidadao_id: int
    nome_unidade: str
    servidor_matricula: int
    evento: str
    mantido: str
    timestamp: str


@dataclass
class DistribuicaoServidores:
    unidades: Dict[str, Dict[str, Dict[str, Servidor]]]
    def adicionar_servidor(self, nome_unidade: str, nome_programa: str, evento: str, servidor: Servidor) -> None:
            if nome_unidade not in self.unidades:
                self.unidades[nome_unidade] = {}
            if nome_programa not in self.unidades[nome_unidade]:
                self.unidades[nome_unidade][nome_programa] = {}
            self.unidades[nome_unidade][nome_programa][evento] = servidor
    def obter_servidor(self, nome_unidade: str, nome_programa: str, evento: str) -> Optional[Servidor]:
            return self.unidades.get(nome_unidade, {}).get(nome_programa, {}).get(evento)

def _convert_sim_time_to_date(sim_time: float) -> str:
    days_elapsed: int = int(math.ceil(sim_time))
    target_date = datetime.now().date() + timedelta(days=days_elapsed)
    return target_date.strftime("%m/%d/%Y")

def _listar_atributos_sociais_possiveis() -> List[str]:
    atributos_possiveis: set = set()
    programas_sociais = CONFIG.sim_programas_sociais
    for programa in programas_sociais:
        atributos_possiveis.update(programa.requisitos.concessao)
        atributos_possiveis.update(programa.requisitos.revisao)
        atributos_possiveis.update(programa.requisitos.pagamento)
    return list(atributos_possiveis)

def _gerar_cidadaos(atributos_sociais_possiveis: List[str]) -> Dict[int, Cidadao]:
    cidadaos: Dict[int, Cidadao] = {}
    for i in range(CONFIG.sim_total_cidadaos):
        # Atribuir um subconjunto aleatório de atributos sociais
        num_atributos: int = random.randint(0, len(atributos_sociais_possiveis))
        atributos_sociais: List[str] = random.sample(atributos_sociais_possiveis, k=num_atributos)

        corruptibilidade: float = round(max(0,random.normalvariate(CONFIG.sim_corruptibilidade_cidadaos_mu, CONFIG.sim_corruptibilidade_cidadaos_sigma)),2)
        cidadaos[i+1] = Cidadao(i + 1, corruptibilidade,atributos_sociais)
    return cidadaos

def _gerar_servidores(logger) -> Tuple[Dict[int, Servidor], DistribuicaoServidores]:
    unidade_programa_etapa_servidor = DistribuicaoServidores(unidades={})
    unidades_gestoras = CONFIG.sim_unidades_gestoras
    servidores: Dict[int, Servidor] = {}
    count_servidores = 0
    for unidade_gestora in unidades_gestoras:
        servidores_unidade: List[Servidor] = []
        for _ in range(unidade_gestora.qtd_servidores):
            corruptibilidade: float = round(max(0, random.normalvariate(CONFIG.sim_corruptibilidade_servidores_mu, CONFIG.sim_corruptibilidade_servidores_sigma)),2)
            servidor = Servidor(unidade_gestora, count_servidores+1, corruptibilidade)
            servidores_unidade.append(servidor)
            servidores[count_servidores+1]=servidor
            count_servidores += 1

        # distribuir servidores por etapas dos processos
        round_robin_servidores = itertools.cycle(servidores_unidade)
        for programa_gerido in unidade_gestora.programas_geridos:
            for evento in CONFIG.sim_eventos:
                unidade_programa_etapa_servidor.adicionar_servidor(
                    unidade_gestora.nome,
                    programa_gerido,
                    evento,
                    next(round_robin_servidores)
                )

    logger.log_info(f"Gerados {len(servidores)} servidores")
    return servidores, unidade_programa_etapa_servidor

def _cidadao_atende_requisitos_etapa(cidadao: Cidadao, requisitos: List[str]) -> bool:
    if not requisitos:
        return True
    return all(req in cidadao.atributos_sociais for req in requisitos)

def _calcular_elegibilidade(cidadao:Cidadao, programa:ProgramaSocial) -> float:
    set_cidadao: set = set(cidadao.atributos_sociais)
    # algumas etapas tem requisitos adicionais
    set_requisitos_todos_eventos = set()
    for evento in CONFIG.sim_eventos:
        if hasattr(programa.requisitos, evento) and asdict(programa.requisitos)[evento]:
            set_requisitos_todos_eventos.update(asdict(programa.requisitos)[evento])

    # % de atendimento dos requisitos
    intersecao: set =  set_cidadao& set_requisitos_todos_eventos
    return len(intersecao) / len(set_requisitos_todos_eventos)

def _sortear_unidade_gestora(nome_programa: str) -> Optional[UnidadeGestora]:
    candidatas: List[UnidadeGestora] = [
        ug for ug in CONFIG.sim_unidades_gestoras if nome_programa in ug.programas_geridos
    ]
    # TODO: tratar como erro de configuração
    if not candidatas:
        return None
    return random.choice(candidatas)

def _cidadao_decidir_programas(logger:'Logger',cidadao: Cidadao,eventos_corruptos:Counter) -> List[EscolhaProgramaUnidade]:
    programas_disponiveis: List[ProgramaSocial] = CONFIG.sim_programas_sociais
    programas_escolhidos: List[EscolhaProgramaUnidade] = []
    for programa_disponivel in programas_disponiveis:
        vai_candidatar = False
        similaridade: float = _calcular_elegibilidade(cidadao, programa_disponivel)
        if similaridade == 1:
            vai_candidatar = True
        else:
            # vies corruptibilidade
            if similaridade + cidadao.corruptibilidade >= 1:
                vai_candidatar = True
                eventos_corruptos['cadastro'] += 1
                logger.log_info(f"Viés de corruptibilidade aplicado em cadastro(Cidadao {cidadao.id}, Programa {programa_disponivel.nome})")

        # escolher unidade
        ug = _sortear_unidade_gestora(programa_disponivel.nome)
        if ug is None:
            logger.log_error(f"Erro de configuração: Unidade gestora não encontrada para programa {programa_disponivel.nome}")
            continue

        if vai_candidatar:
            programas_escolhidos.append(EscolhaProgramaUnidade(programa_disponivel, ug))

    return programas_escolhidos

def _simular_programa(
    logger: Logger,
    env: simpy.Environment,
    cidadao: Cidadao,
    escolha: EscolhaProgramaUnidade,
    distribuicao_servidores: DistribuicaoServidores,
    eventos_gerados: List[Evento],
    eventos_corruptos: Counter) -> Generator[Any, None, None]:
    for nome_evento in CONFIG.sim_eventos:
        if hasattr(escolha.programa.requisitos, nome_evento) and asdict(escolha.programa.requisitos)[nome_evento]:
            duracao_etapa_dias: float = max(1,random.normalvariate(
                CONFIG.sim_eventos_duracao_mu,
                CONFIG.sim_eventos_duracao_sigma
            ))
            yield env.timeout(duracao_etapa_dias)

            # Obter servidor responsável pela etapa do programa
            servidor = distribuicao_servidores.obter_servidor(escolha.unidade_gestora.nome, escolha.programa.nome, nome_evento)
            if servidor is None:
                logger.log_error(f"Servidor não encontrado para a etapa {nome_evento}")
                continue
            # Verificar requisitos para a etapa
            atende_requisitos = _cidadao_atende_requisitos_etapa(cidadao, asdict(escolha.programa.requisitos)[nome_evento])

            # vies corruptibilidade
            bypass = False
            soma_corruptibilidade: float = (
                cidadao.corruptibilidade + servidor.corruptibilidade - escolha.unidade_gestora.conformidade
            )
            if not atende_requisitos and soma_corruptibilidade >= CONFIG.sim_corruptibilidade_limiar:
                bypass = True
                eventos_corruptos[nome_evento] += 1
                logger.log_info(f"Viés de corruptibilidade aplicado em {nome_evento} no {escolha.programa.nome} (C: {cidadao.id}, S:{servidor.id})")

            mantido = "sim" if atende_requisitos or bypass else "não"
            dia_do_evento: str = _convert_sim_time_to_date(env.now)
            evento = Evento(
                escolha.programa.nome,
                cidadao.id,
                escolha.unidade_gestora.nome,
                servidor.id,
                nome_evento,
                mantido,
                dia_do_evento)
            eventos_gerados.append(evento)
            logger.log_info(f"{dia_do_evento}: \u2705 {nome_evento} para cidadão {cidadao.id} em {escolha.programa.nome}")
            if mantido == "não":
                logger.log_info(f"{dia_do_evento}: \u274c {escolha.programa.nome} não mantido em {nome_evento} para cidadao {cidadao.id}")
                break

def _simular_cidadao(
    logger: 'Logger',
    env: simpy.Environment,
    cidadao: Cidadao,
    distribuicao_servidores: DistribuicaoServidores,
    eventos_gerados: List[Evento],
    eventos_corruptos: Counter) -> Generator[Any, None, None]:
    escolhas = _cidadao_decidir_programas(logger,cidadao,eventos_corruptos)
    logger.log_info(f"Cidadão {cidadao.id} escolheu {len(escolhas)} programas")
    processos_etapas: List[Any] = []

    for escolha in escolhas:
        proc = env.process(
            _simular_programa(logger,env, cidadao, escolha, distribuicao_servidores,eventos_gerados,eventos_corruptos))
        processos_etapas.append(proc)
    # Executar todos os programas em paralelo para o cidadão
    for p in processos_etapas:
        yield p

def run_simulation(logger: 'Logger') -> Tuple[List[Evento], Dict[int, Cidadao], Dict[int, Servidor], Counter]:
    logger.log_info(f"Simulação iniciada para {CONFIG.sim_total_cidadaos}")
    atributos_sociais_possiveis = _listar_atributos_sociais_possiveis()
    cidadaos = _gerar_cidadaos(atributos_sociais_possiveis)
    servidores, distribuicao_servidores = _gerar_servidores(logger)

    eventos_gerados: List[Evento] = []
    eventos_corruptos = Counter(
        cadastro=0,
        concessao=0,
        revisao=0,
        pagamento=0
    )
    env: simpy.Environment = simpy.Environment()
    logger.log_info("Starting simulation environment run")
    for _, cidadao in cidadaos.items():
        env.process(_simular_cidadao(logger,env, cidadao, distribuicao_servidores, eventos_gerados, eventos_corruptos))
    env.run()
    logger.log_info(f"Simulação concluída. {len(eventos_gerados)} eventos gerados, dos quais {eventos_corruptos.total()} corruptos.")
    return eventos_gerados, cidadaos, servidores, eventos_corruptos
