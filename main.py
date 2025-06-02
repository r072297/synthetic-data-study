import traceback
import argparse
import sys
from typing import TypedDict

from src import aplicar_prefix_span, gerar_dados_sinteticos, run_pipeline, encontrar_sequencias_curtas
from src.infra import Logger

class ArgsCLI(TypedDict):
    runs: int

def command_generate(args: ArgsCLI) -> None:
    logger = Logger()
    gerar_dados_sinteticos(logger)

def command_analyse(args: ArgsCLI) -> None:
    logger = Logger()
    aplicar_prefix_span(logger)
    encontrar_sequencias_curtas(logger)

def command_pipeline(args: ArgsCLI) -> None:
    run_pipeline(args['runs'])
    return


def main() -> None:
    parser = argparse.ArgumentParser(description="Ferramenta de Simulação e Análise")

    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')

    # Comando generate
    subparsers.add_parser('generate', help='Executar simulação')

    # Comando analyse
    subparsers.add_parser('analyse', help='Executar análise (requer simulação salva)')

    # Comando pipeline
    pipeline_parser = subparsers.add_parser('pipeline', help='Executar pipeline completo')
    pipeline_parser.add_argument('--runs', '-r', type=int, default=3,
                                help='Número de execuções (padrão: 3)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Converter argumentos
    cli_args: ArgsCLI = {'runs': getattr(args, 'runs', 3)}

    try:
        if args.command == 'generate':
            command_generate(cli_args)
        elif args.command == 'analyse':
            command_analyse(cli_args)
        elif args.command == 'pipeline':
            command_pipeline(cli_args)
        else:
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:

        print(f"Erro na simulação: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
