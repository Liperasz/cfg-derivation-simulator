import cyk
from derivation import assign_ids, leftmost_steps
from grammar import load_grammars
from input_reader import read_sentences
from tree_layout import compute_layout


# junta o back: carrega as gramáticas e as sentenças e simula cada uma
# é a única coisa que o front usa, então ele não precisa saber nada de CYK
class Simulator:

    def __init__(self, grammar_path, input_path):

        self.data, self.original, self.cnf = load_grammars(grammar_path)
        self.input_path = input_path

        # erro na gramática para o programa logo no início
        errors = self.original.validate() + self.cnf.validate()
        if errors:
            raise ValueError('Gramática inválida:\n' + '\n'.join(errors))

        if not self.cnf.is_cnf():
            raise ValueError('A gramática da seção "cnf" não está na Forma Normal de Chomsky')

    # textos que o front mostra na tela das gramáticas
    def grammars(self):
        return {
            'name': self.data.get('name', ''),
            'language': self.data.get('language', ''),
            'original': self.original.format_rules(),
            'cnf': self.cnf.format_rules()
        }

    # relê o arquivo toda vez, assim dá pra editar o input sem reiniciar
    def sentences(self):
        return read_sentences(self.input_path)

    # simula uma sentença na FNC e devolve tudo que o front precisa desenhar
    def run(self, word, expected=None):

        result = cyk.parse(self.cnf, word)
        result['expected'] = expected
        result['matches'] = expected is None or expected == result['accepted']

        tree = result['tree']
        if tree is not None:
            assign_ids(tree)
            result['steps'] = leftmost_steps(tree)
            result['layout'] = compute_layout(tree)
        else:
            result['steps'] = []
            result['layout'] = None

        return result

    def run_all(self):
        return [self.run(word, expected) for word, expected in self.sentences()]
