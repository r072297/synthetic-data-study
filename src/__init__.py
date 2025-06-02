from . import infra
from . import servicos
from .gerador import gerar_dados_sinteticos
from .pipeline import run_pipeline
from .analisador import aplicar_prefix_span, encontrar_sequencias_curtas

__version__ = "1.0.0"
__all__ = [
    "infra",
    "servicos",
    "gerar_dados_sinteticos",
    "run_pipeline",
    "aplicar_prefix_span",
    "encontrar_sequencias_curtas"]
