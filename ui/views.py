import pygame

from ui.theme import COLORS, PADDING

# texto mostrado na tela para cada motivo de rejeição devolvido pelo CYK
REASONS = {
    'no_derivation': 'não existe derivação a partir de S (S não aparece no topo da tabela CYK)',
    'invalid_symbol': 'a sentença tem um símbolo fora do alfabeto',
    'empty_not_generated': 'a gramática não tem a produção S → ε'
}


# fundo branco com borda arredondada usado em todos os painéis
def draw_panel(surface, rect):
    pygame.draw.rect(surface, COLORS['panel'], rect, border_radius=10)
    pygame.draw.rect(surface, COLORS['border'], rect, width=1, border_radius=10)


# desenha o texto ancorado no ponto dado (topleft, center, midright...) e devolve o retângulo ocupado
def draw_text(surface, font, text, position, color=None, anchor='topleft'):
    label = font.render(text, True, color or COLORS['text'])
    rect = label.get_rect(**{anchor: position})
    surface.blit(label, rect)
    return rect


# tela com a gramática original e a da FNC lado a lado
def draw_grammars(surface, rect, fonts, grammars):

    # nome do exercício e a linguagem no topo
    title = draw_text(surface, fonts['title'], grammars['name'], (rect.x, rect.y))
    draw_text(surface, fonts['language'], grammars['language'], (rect.x, title.bottom + 6), COLORS['muted'])

    # dois cartões dividindo a largura igualmente
    top = title.bottom + 44
    width = (rect.width - PADDING) // 2
    cards = [
        ('Gramática original', grammars['original'], 'construída a partir da linguagem'),
        ('Gramática na Forma Normal de Chomsky', grammars['cnf'], 'usada na simulação (validada como FNC)')
    ]

    for index, (title_text, rules, caption) in enumerate(cards):

        card = pygame.Rect(rect.x + index * (width + PADDING), top, width, rect.bottom - top)
        draw_panel(surface, card)

        draw_text(surface, fonts['subtitle'], title_text, (card.x + 20, card.y + 16))
        draw_text(surface, fonts['small'], caption, (card.x + 20, card.y + 40), COLORS['muted'])
        pygame.draw.line(surface, COLORS['border'], (card.x, card.y + 66), (card.right, card.y + 66))

        # regras quebradas em mais linhas se não couberem na largura do cartão
        y = card.y + 82
        for rule in rules:
            for line in _wrap_rule(fonts['rule'], rule, card.width - 40):
                draw_text(surface, fonts['rule'], line, (card.x + 20, y))
                y += fonts['rule'].get_linesize() + 4
            y += 6


# quebra "S → XE | XZ | ..." nas barras quando passa da largura
def _wrap_rule(font, rule, max_width):

    # separa a variável das alternativas, e as linhas seguintes ficam alinhadas embaixo da seta
    head, _, body = rule.partition(' → ')
    options = body.split(' | ')
    indent = ' ' * (len(head) + 1) + '| '

    # vai juntando alternativas na linha até não caber mais
    lines = []
    current = f'{head} → {options[0]}'
    for option in options[1:]:
        candidate = f'{current} | {option}'
        if font.size(candidate)[0] > max_width:
            lines.append(current)
            current = f'{indent}{option}'
        else:
            current = candidate
    lines.append(current)

    return lines


# tela da derivação: árvore à esquerda e passos à direita
def draw_derivation(surface, rect, fonts, result, step_index):

    # a lista de passos tem largura fixa e a árvore fica com o resto
    steps_width = 300
    tree_rect = pygame.Rect(rect.x, rect.y, rect.width - steps_width - PADDING, rect.height)
    steps_rect = pygame.Rect(tree_rect.right + PADDING, rect.y, steps_width, rect.height)

    draw_panel(surface, tree_rect)
    draw_panel(surface, steps_rect)

    # sentença rejeitada não tem árvore, só a mensagem com o motivo
    if not result['accepted']:
        _draw_rejected(surface, tree_rect, fonts, result)
        _draw_steps(surface, steps_rect, fonts, [], 0)
        return

    step = result['steps'][step_index]

    # forma sentencial atual em destaque no topo
    draw_text(surface, fonts['small'], 'Forma sentencial', (tree_rect.x + 20, tree_rect.y + 14), COLORS['muted'])
    draw_text(surface, fonts['form'], step['form'], (tree_rect.x + 20, tree_rect.y + 32))
    if step['rule']:
        draw_text(
            surface,
            fonts['body'],
            f'regra aplicada: {step["rule"]}',
            (tree_rect.right - 20, tree_rect.y + 40),
            COLORS['muted'],
            anchor='topright'
        )

    # a árvore ocupa o espaço entre a forma sentencial e a linha de atalhos
    area = pygame.Rect(tree_rect.x, tree_rect.y + 80, tree_rect.width, tree_rect.height - 110).inflate(-40, -40)
    draw_tree(surface, area, fonts, result['tree'], result['layout'], step)

    hint = '← → passos    espaço reproduz    ↑ ↓ sentenças    tab troca de aba'
    draw_text(surface, fonts['small'], hint, (tree_rect.x + 20, tree_rect.bottom - 26), COLORS['muted'])

    _draw_steps(surface, steps_rect, fonts, result['steps'], step_index)


# mensagem centralizada explicando por que a sentença foi rejeitada
def _draw_rejected(surface, rect, fonts, result):

    center_x = rect.centerx
    word = result['word'] or 'ε'

    draw_text(surface, fonts['title'], f'"{word}" é rejeitada', (center_x, rect.centery - 40), COLORS['reject'], 'center')
    draw_text(surface, fonts['body'], REASONS.get(result['reason'], ''), (center_x, rect.centery), COLORS['text'], 'center')
    draw_text(
        surface,
        fonts['small'],
        'veja a aba Tabela CYK para acompanhar o porquê',
        (center_x, rect.centery + 30),
        COLORS['muted'],
        'center'
    )


# desenha só os nós já revelados até o passo atual
def draw_tree(surface, rect, fonts, tree, layout, step):

    visible = set(step['visible'])
    positions = layout['positions']

    # escala as posições abstratas para o retângulo disponível
    x_unit = min(90, rect.width / max(layout['width'] - 1, 1))
    y_unit = min(100, rect.height / max(layout['depth'], 1))
    radius = int(max(12, min(24, x_unit * 0.33, y_unit * 0.3)))

    # centraliza a árvore no retângulo
    tree_width = (layout['width'] - 1) * x_unit
    tree_height = layout['depth'] * y_unit
    offset_x = rect.centerx - tree_width / 2
    offset_y = rect.centery - tree_height / 2

    # converte a posição abstrata do nó em pixels
    def point(node):
        x, y = positions[node.id]
        return int(offset_x + x * x_unit), int(offset_y + y * y_unit)

    # primeiro as arestas, pra ficarem por baixo dos círculos
    nodes = _all_nodes(tree)
    for node in nodes:
        for child in node.children:
            if node.id in visible and child.id in visible:
                pygame.draw.line(surface, COLORS['edge'], point(node), point(child), 2)

    # cor do nó: amarelo = expandido agora, azul = terminal, cinza = ε, branco = variável
    for node in nodes:
        if node.id not in visible:
            continue

        if node.id == step['expanded']:
            fill = COLORS['highlight']
        elif node.is_leaf():
            fill = COLORS['terminal'] if node.symbol != 'ε' else COLORS['node_done']
        else:
            fill = COLORS['node']

        center = point(node)
        pygame.draw.circle(surface, fill, center, radius)
        pygame.draw.circle(surface, COLORS['text'], center, radius, 2)
        draw_text(surface, fonts['node'], node.symbol, center, anchor='center')


# lista todos os nós da árvore (a ordem não importa pro desenho)
def _all_nodes(tree):

    nodes = []
    stack = [tree]
    while stack:
        node = stack.pop()
        nodes.append(node)
        stack.extend(node.children)

    return nodes


# lista "S ⇒ XE ⇒ ..." com o passo atual destacado
def _draw_steps(surface, rect, fonts, steps, step_index):

    draw_text(surface, fonts['subtitle'], 'Derivação mais à esquerda', (rect.x + 16, rect.y + 14))

    if not steps:
        draw_text(surface, fonts['body'], 'sem derivação', (rect.x + 16, rect.y + 50), COLORS['muted'])
        return

    # quantas linhas cabem no painel
    line_height = 44
    list_top = rect.y + 48
    visible_count = max(1, (rect.bottom - list_top - 10) // line_height)

    # mantém o passo atual dentro da área visível
    first = max(0, min(step_index - visible_count + 2, len(steps) - visible_count))

    for index in range(first, min(len(steps), first + visible_count)):

        step = steps[index]
        row = pygame.Rect(rect.x + 8, list_top + (index - first) * line_height, rect.width - 16, line_height - 4)

        # passo atual destacado e passos futuros em cinza
        if index == step_index:
            pygame.draw.rect(surface, COLORS['highlight'], row, border_radius=6)

        color = COLORS['text'] if index <= step_index else COLORS['muted']
        prefix = '' if index == 0 else '⇒ '
        draw_text(surface, fonts['step'], f'{prefix}{step["form"]}', (row.x + 8, row.y + 2), color)
        if step['rule']:
            draw_text(surface, fonts['small'], step['rule'], (row.x + 30, row.y + 22), COLORS['muted'])


# tabela triangular do CYK (linha de baixo = trechos de tamanho 1)
def draw_cyk_table(surface, rect, fonts, result):

    draw_panel(surface, rect)
    word = result['word']

    title = f'Tabela CYK de "{word or "ε"}"'
    draw_text(surface, fonts['subtitle'], title, (rect.x + 20, rect.y + 16))

    # palavra vazia ou com símbolo inválido não chega a montar tabela
    if result['reason'] == 'invalid_symbol' or not word:
        message = REASONS.get(result['reason']) or 'a sentença vazia é aceita direto por S → ε'
        draw_text(surface, fonts['body'], message, rect.center, COLORS['muted'], 'center')
        return

    # tamanho das células conforme o espaço e o tamanho da palavra, tabela centralizada
    table = result['table']
    n = len(word)
    area = pygame.Rect(rect.x + 60, rect.y + 60, rect.width - 100, rect.height - 120)
    cell_width = min(130, area.width // n)
    cell_height = min(60, area.height // n)
    left = area.centerx - cell_width * n // 2
    bottom = area.y + cell_height * n

    for length in range(1, n + 1):
        for start in range(n - length + 1):

            # quanto maior o trecho, mais alta a linha (a de tamanho n fica no topo)
            cell = pygame.Rect(left + start * cell_width, bottom - length * cell_height, cell_width, cell_height)
            variables = table[length - 1][start]

            # a célula do topo decide: verde se tem S, vermelho se não tem
            if length == n:
                accepted = result['accepted']
                fill = COLORS['accept_soft'] if accepted else COLORS['reject_soft']
                pygame.draw.rect(surface, fill, cell)

            # ∅ quando nenhuma variável gera aquele trecho
            pygame.draw.rect(surface, COLORS['border'], cell, 1)
            text = ', '.join(variables) if variables else '∅'
            color = COLORS['text'] if variables else COLORS['muted']
            draw_text(surface, _fit_font(fonts, text, cell_width - 8), text, cell.center, color, 'center')

        # rótulo do tamanho do trecho à esquerda da linha
        draw_text(
            surface,
            fonts['small'],
            f'{length}',
            (left - 12, bottom - length * cell_height + cell_height // 2),
            COLORS['muted'],
            'midright'
        )

    # letras da palavra embaixo de cada coluna
    for index, symbol in enumerate(word):
        draw_text(surface, fonts['rule'], symbol, (left + index * cell_width + cell_width // 2, bottom + 18), anchor='center')

    caption = 'linha = tamanho do trecho, coluna = posição inicial'
    draw_text(surface, fonts['small'], caption, (rect.centerx, rect.bottom - 22), COLORS['muted'], 'center')


# usa a fonte menor quando o texto não cabe na célula
def _fit_font(fonts, text, width):
    return fonts['body'] if fonts['body'].size(text)[0] <= width else fonts['small']
