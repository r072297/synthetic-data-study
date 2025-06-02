# Documentação do Projeto Synthetic-Data-Study

## Visão Geral

O **Synthetic-Data-Study** é um sistema de simulação e análise de interações entre cidadãos e programas sociais governamentais, desenvolvido como parte de um Trabalho de Conclusão de Curso (TCC). O projeto utiliza simulação baseada em eventos discretos para modelar comportamentos de cidadãos e servidores públicos, incluindo aspectos de corrupção, e aplica algoritmos de mineração de padrões sequenciais para identificar comportamentos e anomalias nos processos.

Os resultados da mineração são comparados com a fonte da verdade em `eventos_corruptos.json` para averiguar sua efetividade.

## Objetivos do Projeto

### Objetivo Principal
O objetivo do projeto e analisar a adequação do uso de dados sintéticos no teste de soluções de mineração de padrões em sequências.

### Objetivos Específicos
- Modelar o comportamento de cidadãos na busca por benefícios sociais
- Simular o processamento de solicitações a cada benefício pleiteado
- Incorporar fatores de corruptibilidade no modelo de simulação
- Aplicar algoritmos de mineração de padrões sequenciais (SPMF) nos dados simulados
- Comparar os padrões identificados com a fonte da verdade em `eventos_corruptos.json`

## Arquitetura do Sistema

O projeto é estruturado da seguinte forma:

```
cz-sim-study/
├── src/
│   ├── gerador.py          # Simulação de dados
│   ├── analisador.py       # Análise com SPMF
│   ├── pipeline.py         # Execução completa
│   ├── servicos/           # Lógica de negócio
│   │   ├── simulacao.py    # Motor de simulação
│   │   ├── pre_processamento.py  # Preparação para análise
│   │   └── analise.py      # Análises específicas
│   └── infra/              # Infraestrutura
│       ├── config.py       # Configurações
│       ├── filesystem.py   # Operações de arquivo
│       ├── logger.py       # Sistema de logs
│       └── spmf_adapter.py # Interface com SPMF
└── data/                   # Dados simulados e resultados
```

## Componentes Principais

### 1. Motor de Simulação (`simulacao.py`)
- **Geração de Cidadãos**: Cria população com atributos sociais variados
- **Geração de Servidores**: Distribui servidores por unidades gestoras
- **Simulação de Eventos**: Modela processos de cadastro, concessão, revisão e pagamento
- **Modelagem de Corrupção**: Incorpora fatores de corruptibilidade

### 2. Pré-processamento (`pre_processamento.py`)
- **Conversão de Dados**: Transforma eventos em sequências para análise
- **Formatação SPMF**: Prepara dados no formato esperado pelo SPMF
- **Tradução de Itens**: Converte eventos em códigos numéricos

### 3. Análise com SPMF (`spmf_adapter.py`)
- **Integração SPMF**: Interface com a ferramenta de mineração
- **Algoritmo PrefixSpan**: Mineração de padrões sequenciais
- **Processamento de Resultados**: Interpretação dos padrões encontrados

## Processos Simulados

### Programas Sociais Modelados
1. **Auxílio Alimentação**
   - Órgão: Secretaria de Assistência Social
   - Requisitos:
     - Concessão: baixa_renda
     - Revisão: baixa_renda
     - Pagamento: baixa_renda

2. **Auxílio Creche**
   - Órgão: Secretaria de Educação
   - Requisitos:
     - Concessão: idade, baixa_renda, filhos_menores
     - Revisão: idade, baixa_renda, filhos_menores
     - Pagamento: idade, baixa_renda, filhos_menores, frequencia_creche

3. **Bolsa Estudantil**
   - Órgão: Secretaria de Educação
   - Requisitos:
     - Concessão: idade, baixa_renda, matricula
     - Revisão: idade, baixa_renda, matricula
     - Pagamento: idade, baixa_renda, matricula, frequencia_escolar

### Etapas dos Processos
Cada programa social passa por quatro etapas principais:

1. **Cadastro**: Registro inicial do cidadão no sistema
2. **Concessão**: Avaliação e aprovação do benefício
3. **Revisão**: Verificação periódica de elegibilidade
4. **Pagamento**: Liberação do benefício

### Unidades Gestoras
- **UG Assistência Social**: Gerencia Auxílio Alimentação
- **UG Educação**: Gerencia Bolsa Estudantil e Auxílio Creche

## Modelagem da Corrupção

### Fatores de Corruptibilidade
- **Cidadãos**: Tendência a fornecer informações incorretas (μ=0.4, σ=0.3)
- **Servidores**: Propensão a aceitar irregularidades (μ=0.2, σ=0.15)
- **Unidades Gestoras**: Nível de conformidade organizacional

### Aplicação dos Vieses
- **Cadastro**: Cidadão se inscreve mesmo sem atender todos os requisitos
- **Outras Etapas**: Servidor aprova mesmo com requisitos não atendidos
- **Limiar**: Soma (corruptibilidade_cidadão + corruptibilidade_servidor - conformidade_unidade) ≥ 0.6

## Análise de Padrões

### Algoritmo PrefixSpan
- **Objetivo**: Identificar sequências frequentes de eventos
- **Suporte Mínimo**: 10% (configurável)
- **Comprimento Máximo**: 20 eventos por sequência

### Dados Analisados
- **Eventos**: cadastro, concessao, revisao, pagamento
- **Unidades**: nome da unidade gestora
- **Status**: mantido/não mantido em cada etapa

### Interpretação dos Resultados
Sequências de corrupção:
- curta: para na revisão
- longa: passa da revisão

## Como Usar

### Execução Individual
```bash
# Instalar com pipenv
pipenv install

# Gerar dados simulados
python main.py generate

# Executar análise
python main.py analyse

# Pipeline completo
python main.py pipeline --runs 5
```

### Configuração
O arquivo `src/infra/config.py` contém todas as configurações do sistema:
- Parâmetros de simulação
- Configurações de análise
- Estrutura dos programas sociais

## Resultados Gerados

### Dados de Simulação
- `cidadaos.json`: Dados dos cidadãos simulados
- `servidores.json`: Dados dos servidores
- `eventos.json`: Todos os eventos da simulação
- `eventos_corruptos.json`: Estatísticas de corrupção

### Resultados de Análise
- `spmf_input.txt`: Dados formatados para o SPMF
- `spmf_output.txt`: Padrões sequenciais identificados
- 'simulação

## Tecnologias Utilizadas

- **Python 3.13+**: Linguagem principal
- **SimPy**: Simulação de eventos discretos
- **MyPy**: Verificação de tipos estáticos
- **Pipenv**: Gerenciamento de dependências
- **SPMF**: Framework de mineração de padrões
- **grep**: Busca de padrões regex em arquivos
