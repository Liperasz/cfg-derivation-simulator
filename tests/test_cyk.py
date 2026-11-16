import itertools
import os
import sys
import unittest

# coloca a raiz do projeto no path pra conseguir importar os módulos
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

import cyk
from grammar import Grammar, load_grammars
from simulator import Simulator

GRAMMAR_PATH = os.path.join(ROOT_DIR, 'data', 'grammar.json')
INPUT_PATH = os.path.join(ROOT_DIR, 'data', 'input.txt')
MAX_LENGTH = 8


# definição direta de L₅, usada pra conferir a gramática
def in_language(word):

    # precisa ter o formato a*b*c*
    if list(word) != sorted(word):
        return False

    i, j, k = word.count('a'), word.count('b'), word.count('c')

    return i == j + k or k == i + j


# gera por força bruta as palavras da gramática original até um tamanho máximo
def generate_original(grammar, max_length):

    words = set()
    seen = set()
    forms = [(grammar.start,)]

    while forms:

        form = forms.pop()
        if form in seen:
            continue
        seen.add(form)

        # forma sem variáveis é uma palavra
        index = next((i for i, symbol in enumerate(form) if symbol in grammar.variables), None)
        if index is None:
            words.add(''.join(form))
            continue

        # poda: os terminais já presentes passaram do limite
        if sum(symbol in grammar.terminals for symbol in form) > max_length:
            continue

        for body in grammar.productions[form[index]]:
            new_form = form[:index] + body + form[index + 1:]
            if len(new_form) <= max_length + 2:
                forms.append(new_form)

    return {word for word in words if len(word) <= max_length}


class TestCyk(unittest.TestCase):

    # o simulador é criado uma vez só pra todos os testes
    @classmethod
    def setUpClass(cls):
        cls.simulator = Simulator(GRAMMAR_PATH, INPUT_PATH)
        cls.cnf = cls.simulator.cnf
        cls.original = cls.simulator.original

    # a original não está na FNC (tem produções unitárias e de 3 símbolos), a FNC sim
    def test_grammars_are_valid(self):
        self.assertEqual(self.original.validate(), [])
        self.assertEqual(self.cnf.validate(), [])
        self.assertTrue(self.cnf.is_cnf())
        self.assertFalse(self.original.is_cnf())

    # todas as sentenças do arquivo de entrada dão o resultado esperado
    def test_input_sentences(self):
        for result in self.simulator.run_all():
            with self.subTest(word=result['word']):
                self.assertTrue(result['matches'])

    # testa todas as palavras sobre {a, b, c} até MAX_LENGTH no CYK contra a definição de L₅
    def test_cnf_generates_l5(self):
        for length in range(MAX_LENGTH + 1):
            for letters in itertools.product('abc', repeat=length):
                word = ''.join(letters)
                with self.subTest(word=word):
                    self.assertEqual(cyk.parse(self.cnf, word)['accepted'], in_language(word))

    # a gramática original gera exatamente as mesmas palavras de L₅ até MAX_LENGTH
    def test_original_generates_l5(self):
        expected = {
            ''.join(letters)
            for length in range(MAX_LENGTH + 1)
            for letters in itertools.product('abc', repeat=length)
            if in_language(''.join(letters))
        }
        self.assertEqual(generate_original(self.original, MAX_LENGTH), expected)

    # mesma árvore da Figura 10 do relatório
    def test_report_trees(self):
        aabc = self.simulator.run('aabc')
        self.assertEqual([step['rule'] for step in aabc['steps'][1:3]], ['S → XE', 'X → a'])
        self.assertEqual(aabc['steps'][-1]['form'], 'aabc')

        abcc = self.simulator.run('abcc')
        self.assertEqual(abcc['steps'][3]['rule'], 'G → BZ')

    # ε é aceita direto por S → ε, numa derivação de um passo
    def test_empty_word(self):
        result = self.simulator.run('')
        self.assertTrue(result['accepted'])
        self.assertEqual([step['form'] for step in result['steps']], ['S', 'ε'])

    # símbolo fora do alfabeto rejeita e indica a posição
    def test_invalid_symbol(self):
        result = cyk.parse(self.cnf, 'abd')
        self.assertFalse(result['accepted'])
        self.assertEqual(result['reason'], 'invalid_symbol')
        self.assertEqual(result['error_position'], 2)

    # o programa também funciona com outra gramática (aⁿbⁿ)
    def test_example_grammar(self):
        _, original, cnf = load_grammars(os.path.join(ROOT_DIR, 'data', 'grammar.example.json'))
        self.assertTrue(cnf.is_cnf())
        for word, accepted in [('', True), ('ab', True), ('aabb', True), ('aab', False), ('ba', False)]:
            self.assertEqual(cyk.parse(cnf, word)['accepted'], accepted)

    # S aparece do lado direito, então S → ε não é permitido na FNC
    def test_not_cnf(self):
        grammar = Grammar('', ['S', 'A'], ['a'], 'S', {'S': ['AS', 'ε'], 'A': ['a']})
        self.assertFalse(grammar.is_cnf())


if __name__ == '__main__':
    unittest.main()
