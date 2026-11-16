from grammar import EPSILON, ARROW


# nó da árvore de derivação (folha = terminal ou ε)
class Node:

    def __init__(self, symbol, children=None):

        self.id = None
        self.symbol = symbol
        self.children = children or []

    # na árvore final, só terminais e ε ficam sem filhos
    def is_leaf(self):
        return not self.children

    # lado direito usado pra expandir o nó, ex.: "A → XY"
    def rule(self):
        body = ''.join(child.symbol for child in self.children if child.symbol != EPSILON) or EPSILON
        return f'{self.symbol} {ARROW} {body}'

    # versão em dicionário da árvore (útil pra depurar ou salvar em json)
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'children': [child.to_dict() for child in self.children]
        }


# numera os nós em pré-ordem (a numeração é usada pelo front pra animar)
def assign_ids(root):

    # pilha com os filhos invertidos pra visitar da esquerda pra direita
    nodes = []
    stack = [root]

    while stack:
        node = stack.pop()
        node.id = len(nodes)
        nodes.append(node)
        stack.extend(reversed(node.children))

    return nodes


# gera a derivação mais à esquerda, um passo por variável expandida
def leftmost_steps(root):

    # a forma sentencial é uma lista de nós, então dá pra saber de onde veio cada símbolo
    form = [root]
    visible = {root.id}
    steps = [{
        'form': _form_text(form),
        'expanded': None,
        'rule': None,
        'visible': sorted(visible)
    }]

    while True:

        # pega a variável mais à esquerda que ainda não foi expandida
        index = next((i for i, node in enumerate(form) if not node.is_leaf()), None)
        if index is None:
            break

        # troca a variável pelos filhos dela e revela os filhos na árvore
        node = form[index]
        form = form[:index] + node.children + form[index + 1:]
        visible.update(child.id for child in node.children)

        steps.append({
            'form': _form_text(form),
            'expanded': node.id,
            'rule': node.rule(),
            'visible': sorted(visible)
        })

    return steps


# forma sentencial como texto (o ε some quando tem outros símbolos junto)
def _form_text(form):
    return ''.join(node.symbol for node in form if node.symbol != EPSILON) or EPSILON
