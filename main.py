import argparse
import os
import sys

from ui.app import App
from core.simulator import Simulator

# caminhos relativos ao arquivo, assim o programa roda de qualquer pasta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_GRAMMAR = os.path.join(BASE_DIR, 'data', 'grammar.json')
DEFAULT_INPUT = os.path.join(BASE_DIR, 'data', 'input.txt')


# argumentos opcionais: sem eles usa a gramática e as sentenças da pasta data
def parse_args():

    parser = argparse.ArgumentParser(description='Simulador de derivação de uma GLC na Forma Normal de Chomsky')
    parser.add_argument('grammar', nargs='?', default=DEFAULT_GRAMMAR, help='arquivo JSON da gramática')
    parser.add_argument('input', nargs='?', default=DEFAULT_INPUT, help='arquivo com as sentenças')

    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    # erro de arquivo ou de gramática sai com mensagem, sem abrir a janela
    try:
        simulator = Simulator(args.grammar, args.input)
        simulator.sentences()
    except (OSError, ValueError, KeyError) as err:
        print(f'[Erro] {err}')
        sys.exit(1)

    App(simulator).run()
