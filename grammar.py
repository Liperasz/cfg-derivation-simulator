import json

EPSILON = 'ε'
ARROW = '→'


# guarda uma gramática (variáveis, terminais, produções e símbolo inicial)
class Grammar:

    def __init__(self, name, variables, terminals, start, productions):

        self.name = name
        self.variables = list(variables)
        self.terminals = list(terminals)
        self.start = start

        # cada lado direito vira uma tupla de símbolos, e ε vira a tupla vazia
        self.productions = {
            variable: [self._parse_body(body) for body in bodies]
            for variable, bodies in productions.items()
        }

    # "aAc" vira ('a', 'A', 'c'), já que cada símbolo tem um caractere
    @staticmethod
    def _parse_body(body):
        return () if body == EPSILON else tuple(body)

    # monta a gramática a partir de uma seção ('original' ou 'cnf') do json
    @classmethod
    def from_dict(cls, data, section):

        grammar_data = data[section]

        return cls(
            name=data.get('name', ''),
            variables=grammar_data['variables'],
            terminals=data['terminals'],
            start=data['start'],
            productions=grammar_data['productions']
        )

    # devolve a lista de erros encontrados (lista vazia = gramática válida)
    def validate(self):

        errors = []

        # variáveis e terminais precisam ser símbolos de um caractere, sem conflito entre si
        for symbol in self.variables + self.terminals:
            if len(symbol) != 1:
                errors.append(f'O símbolo {symbol!r} não tem exatamente um caractere')

        # um mesmo símbolo não pode ser variável e terminal
        overlap = set(self.variables) & set(self.terminals)
        if overlap:
            errors.append(f'Símbolos usados como variável e terminal: {sorted(overlap)}')

        if self.start not in self.variables:
            errors.append(f'O símbolo inicial {self.start!r} não está nas variáveis')

        # todo símbolo do lado direito precisa ser conhecido
        known = set(self.variables) | set(self.terminals)
        for variable, bodies in self.productions.items():

            if variable not in self.variables:
                errors.append(f'A produção de {variable!r} usa uma variável não declarada')

            for body in bodies:
                unknown = [symbol for symbol in body if symbol not in known]
                if unknown:
                    errors.append(f'{variable} {ARROW} {"".join(body)} usa símbolos desconhecidos: {unknown}')

        return errors

    # verifica se está na FNC: A → BC, A → a, e S → ε só se S não aparece à direita
    def is_cnf(self):

        # S → ε só é permitido se S não aparecer no lado direito de nenhuma produção
        start_on_right = any(
            self.start in body
            for bodies in self.productions.values()
            for body in bodies
        )

        for variable, bodies in self.productions.items():
            for body in bodies:

                # produção vazia
                if len(body) == 0:
                    if variable != self.start or start_on_right:
                        return False

                # A → a
                elif len(body) == 1:
                    if body[0] not in self.terminals:
                        return False

                # A → BC
                elif len(body) == 2:
                    if body[0] not in self.variables or body[1] not in self.variables:
                        return False

                # três ou mais símbolos nunca estão na FNC
                else:
                    return False

        return True

    # linhas no formato "S → XE | XZ | ε", na ordem das variáveis
    def format_rules(self):

        lines = []
        for variable in self.variables:
            bodies = self.productions.get(variable, [])
            if bodies:
                options = ' | '.join(''.join(body) or EPSILON for body in bodies)
                lines.append(f'{variable} {ARROW} {options}')

        return lines


# lê o json e devolve as duas gramáticas (original e na FNC)
def load_grammars(path):

    with open(path, 'r', encoding='utf-8') as grammar_file:
        data = json.load(grammar_file)

    original = Grammar.from_dict(data, 'original')
    cnf = Grammar.from_dict(data, 'cnf')

    return data, original, cnf
