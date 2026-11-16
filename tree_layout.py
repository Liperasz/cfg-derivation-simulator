# calcula a posição de cada nó: folhas lado a lado e o pai no meio dos filhos
# x em "unidades de folha" e y em níveis, o front só escala pro tamanho da tela
def compute_layout(root):

    positions = {}
    next_leaf = [0]

    def place(node, depth):

        if node.is_leaf():
            x = next_leaf[0]
            next_leaf[0] += 1

        else:
            xs = [place(child, depth + 1) for child in node.children]
            x = (xs[0] + xs[-1]) / 2

        positions[node.id] = (x, depth)
        return x

    place(root, 0)

    width = next_leaf[0]
    depth = max(y for _, y in positions.values())

    return {
        'positions': positions,
        'width': width,
        'depth': depth
    }
