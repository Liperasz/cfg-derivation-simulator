from derivation import Node
from grammar import EPSILON


# roda o CYK na palavra e devolve o resultado com a árvore (se existir) e a tabela
def parse(grammar, word):

    result = {
        'word': word,
        'accepted': False,
        'tree': None,
        'table': [],
        'reason': None,
        'error_position': None
    }

    # símbolo fora do alfabeto já rejeita
    for position, symbol in enumerate(word):
        if symbol not in grammar.terminals:
            result['reason'] = 'invalid_symbol'
            result['error_position'] = position
            return result

    # a palavra vazia só é gerada por S → ε
    if word == '':
        if () in grammar.productions.get(grammar.start, []):
            result['accepted'] = True
            result['tree'] = Node(grammar.start, [Node(EPSILON)])
        else:
            result['reason'] = 'empty_not_generated'
        return result

    table = _fill_table(grammar, word)
    result['table'] = _table_for_display(grammar, table)

    # aceita se S está na célula que cobre a palavra inteira
    if grammar.start in table[len(word) - 1][0]:
        result['accepted'] = True
        result['tree'] = _build_tree(table, grammar.start, 0, len(word))
    else:
        result['reason'] = 'no_derivation'

    return result


# table[length - 1][start] = {variável: backpointer}, só o primeiro backpointer achado
def _fill_table(grammar, word):

    n = len(word)
    table = [[{} for _ in range(n - length + 1)] for length in range(1, n + 1)]

    # linha de baixo: variáveis que geram cada terminal direto (A → a)
    for i, symbol in enumerate(word):
        for variable in grammar.variables:
            if (symbol,) in grammar.productions.get(variable, []):
                table[0][i][variable] = ('terminal', symbol)

    # demais linhas: A → BC com B cobrindo o começo e C o resto do trecho
    for length in range(2, n + 1):
        for start in range(n - length + 1):

            cell = table[length - 1][start]
            for variable in grammar.variables:
                for body in grammar.productions.get(variable, []):

                    if len(body) != 2 or variable in cell:
                        continue

                    # a ordem das produções no json decide qual árvore aparece
                    for left_length in range(1, length):
                        left = table[left_length - 1][start]
                        right = table[length - left_length - 1][start + left_length]

                        if body[0] in left and body[1] in right:
                            cell[variable] = ('binary', body, left_length)
                            break

    return table


# reconstrói a árvore seguindo os backpointers
def _build_tree(table, variable, start, length):

    pointer = table[length - 1][start][variable]

    if pointer[0] == 'terminal':
        return Node(variable, [Node(pointer[1])])

    _, body, left_length = pointer
    left = _build_tree(table, body[0], start, left_length)
    right = _build_tree(table, body[1], start + left_length, length - left_length)

    return Node(variable, [left, right])


# só os nomes das variáveis de cada célula, na ordem da gramática
def _table_for_display(grammar, table):
    return [
        [[variable for variable in grammar.variables if variable in cell] for cell in row]
        for row in table
    ]
