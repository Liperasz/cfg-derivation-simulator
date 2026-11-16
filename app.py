import os

import pygame

import views
from theme import (
    COLORS,
    CONTROLS_HEIGHT,
    FPS,
    HEADER_HEIGHT,
    MIN_WINDOW_SIZE,
    PADDING,
    SIDEBAR_WIDTH,
    STEP_INTERVAL,
    WINDOW_SIZE,
    load_fonts
)
from widgets import Button, SentenceList

TABS = ['Gramáticas', 'Derivação', 'Tabela CYK']


# interface em pygame: só desenha o que o Simulator devolve
class App:

    def __init__(self, simulator):

        pygame.init()
        pygame.display.set_caption('Simulador de Derivação - GLC na FNC')
        self.screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.fonts = load_fonts()

        self.simulator = simulator
        self.grammars = simulator.grammars()
        self.results = simulator.run_all()

        # estado da tela
        self.tab = 0
        self.selected = 0
        self.step = 0
        self.playing = False
        self.timer = 0.0
        self.running = True

        # componentes da tela (a posição de cada um é definida na hora de desenhar)
        self.sentence_list = SentenceList(self.select)
        self.tab_buttons = [Button(name, lambda index=index: self.set_tab(index)) for index, name in enumerate(TABS)]
        self.control_buttons = [
            Button('Início', self.first_step),
            Button('Anterior', self.previous_step),
            Button('Reproduzir', self.toggle_play),
            Button('Próximo', self.next_step),
            Button('Fim', self.last_step)
        ]
        self.reload_button = Button('Recarregar entrada (F5)', self.reload)

    # resultado da sentença selecionada (None se o arquivo estiver vazio)
    @property
    def result(self):
        return self.results[self.selected] if self.results else None

    # loop principal: trata os eventos, atualiza a animação e redesenha a tela
    def run(self):

        while self.running:

            # tempo do último quadro em segundos (usado no modo reprodução)
            delta = self.clock.tick(FPS) / 1000
            self.handle_events()
            self.update(delta)
            self.draw()
            pygame.display.flip()

        pygame.quit()

    # o resto da divisão faz a troca de aba dar a volta (da última volta pra primeira)
    def set_tab(self, index):
        self.tab = index % len(TABS)

    # troca a sentença selecionada e volta a derivação pro começo
    def select(self, index):

        if not self.results:
            return

        # mesmo esquema da aba, ↑ na primeira sentença vai pra última
        self.selected = index % len(self.results)
        self.sentence_list.ensure_visible(self.selected)

        self.step = 0
        self.playing = False

    # quantidade de passos da derivação (sentença rejeitada não tem nenhum)
    def step_count(self):
        return len(self.result['steps']) if self.result else 0

    def first_step(self):
        self.step = 0
        self.playing = False

    def last_step(self):
        self.step = max(self.step_count() - 1, 0)
        self.playing = False

    def previous_step(self):
        self.step = max(self.step - 1, 0)
        self.playing = False

    # para no último passo (não passa do fim da derivação)
    def next_step(self):
        self.step = min(self.step + 1, max(self.step_count() - 1, 0))

    # liga e desliga a reprodução automática dos passos
    def toggle_play(self):

        # se já estava no fim, recomeça do primeiro passo
        if not self.playing and self.step >= self.step_count() - 1:
            self.step = 0

        self.playing = not self.playing
        self.timer = 0.0

    # relê o arquivo de sentenças (dá pra editar com o programa aberto)
    def reload(self):

        self.results = self.simulator.run_all()

        # a lista pode ter diminuído, então a seleção não pode passar do fim
        self.select(min(self.selected, max(len(self.results) - 1, 0)))

    # distribui cada evento do pygame pra função que trata ele
    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            # redimensionar recria a janela, respeitando o tamanho mínimo
            elif event.type == pygame.VIDEORESIZE:
                size = (max(event.w, MIN_WINDOW_SIZE[0]), max(event.h, MIN_WINDOW_SIZE[1]))
                self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)

            # só o botão esquerdo do mouse conta como clique
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)

            # a rolagem só é usada na lista de sentenças
            elif event.type == pygame.MOUSEWHEEL:
                self.sentence_list.wheel(event.y, len(self.results))

            elif event.type == pygame.KEYDOWN:
                self.handle_key(event.key)

    # testa o clique nos botões e, se não acertou nenhum, na lista de sentenças
    def handle_click(self, position):

        # os controles da derivação só existem na aba Derivação e com sentença aceita
        buttons = self.tab_buttons + [self.reload_button]
        if self.tab == 1 and self.result and self.result['accepted']:
            buttons += self.control_buttons

        for button in buttons:
            if button.click(position):
                return

        self.sentence_list.click(position, len(self.results))

    # tabela de atalhos: cada tecla aponta pra mesma ação do botão equivalente
    def handle_key(self, key):

        actions = {
            pygame.K_ESCAPE: self.quit,
            pygame.K_LEFT: self.previous_step,
            pygame.K_RIGHT: self.next_step,
            pygame.K_HOME: self.first_step,
            pygame.K_END: self.last_step,
            pygame.K_SPACE: self.toggle_play,
            pygame.K_r: self.first_step,
            pygame.K_F5: self.reload,
            pygame.K_UP: lambda: self.select(self.selected - 1),
            pygame.K_DOWN: lambda: self.select(self.selected + 1),
            pygame.K_TAB: lambda: self.set_tab(self.tab + 1),
            pygame.K_1: lambda: self.set_tab(0),
            pygame.K_2: lambda: self.set_tab(1),
            pygame.K_3: lambda: self.set_tab(2)
        }

        if key in actions:
            actions[key]()

    def quit(self):
        self.running = False

    # avança sozinho no modo reprodução
    def update(self, delta):

        if not self.playing:
            return

        # acumula o tempo e só avança quando passa do intervalo entre passos
        self.timer += delta
        if self.timer >= STEP_INTERVAL:
            self.timer = 0.0
            self.next_step()

            # chegou no último passo, então para sozinho
            if self.step >= self.step_count() - 1:
                self.playing = False

    # redesenha a tela inteira a cada quadro (cabeçalho, lateral e a aba atual)
    def draw(self):

        width, height = self.screen.get_size()
        self.screen.fill(COLORS['background'])

        self.draw_header(width)
        self.draw_sidebar(height)

        # área à direita da lateral, onde fica o conteúdo da aba
        content = pygame.Rect(
            SIDEBAR_WIDTH + 2 * PADDING,
            HEADER_HEIGHT + PADDING,
            width - SIDEBAR_WIDTH - 3 * PADDING,
            height - HEADER_HEIGHT - 2 * PADDING
        )

        # a aba de gramáticas não depende de sentença, as outras sim
        if self.tab == 0:
            views.draw_grammars(self.screen, content.inflate(-8, -8), self.fonts, self.grammars)

        elif not self.result:
            views.draw_text(self.screen, self.fonts['body'], 'Nenhuma sentença no arquivo', content.center, anchor='center')

        elif self.tab == 1:
            self.draw_derivation_tab(content)

        else:
            views.draw_cyk_table(self.screen, content, self.fonts, self.result)

    # faixa do topo com o título e as abas
    def draw_header(self, width):

        pygame.draw.rect(self.screen, COLORS['panel'], (0, 0, width, HEADER_HEIGHT))
        pygame.draw.line(self.screen, COLORS['border'], (0, HEADER_HEIGHT), (width, HEADER_HEIGHT))

        views.draw_text(self.screen, self.fonts['title'], 'Simulador de Derivação', (PADDING, 12))
        views.draw_text(
            self.screen,
            self.fonts['small'],
            'Gramática Livre de Contexto na Forma Normal de Chomsky',
            (PADDING, 40),
            COLORS['muted']
        )

        # abas alinhadas à direita do cabeçalho (posicionadas da última pra primeira)
        x = width - PADDING
        for button in reversed(self.tab_buttons):
            button_width = self.fonts['body'].size(button.label)[0] + 32
            x -= button_width
            button.rect = pygame.Rect(x, 14, button_width, 36)
            x -= 8

        # a aba atual fica preenchida
        for index, button in enumerate(self.tab_buttons):
            button.active = index == self.tab
            button.draw(self.screen, self.fonts['body'])

    # painel da esquerda: lista de sentenças, resumo e botão de recarregar
    def draw_sidebar(self, height):

        sidebar = pygame.Rect(PADDING, HEADER_HEIGHT + PADDING, SIDEBAR_WIDTH, height - HEADER_HEIGHT - 2 * PADDING)
        views.draw_panel(self.screen, sidebar)

        # título e nome do arquivo de entrada
        views.draw_text(self.screen, self.fonts['subtitle'], 'Sentenças', (sidebar.x + 14, sidebar.y + 12))
        file_name = os.path.basename(self.simulator.input_path)
        views.draw_text(self.screen, self.fonts['small'], file_name, (sidebar.x + 14, sidebar.y + 34), COLORS['muted'])

        # resumo de quantas bateram com o esperado
        matches = sum(result['matches'] for result in self.results)
        summary_color = COLORS['accept'] if matches == len(self.results) else COLORS['reject']
        summary = f'{matches}/{len(self.results)} conforme o esperado'
        views.draw_text(self.screen, self.fonts['small'], summary, (sidebar.x + 14, sidebar.bottom - 74), summary_color)

        # os retângulos são recalculados todo quadro porque a janela pode mudar de tamanho
        self.reload_button.rect = pygame.Rect(sidebar.x + 12, sidebar.bottom - 50, sidebar.width - 24, 36)
        self.reload_button.draw(self.screen, self.fonts['small'])

        self.sentence_list.rect = pygame.Rect(sidebar.x + 10, sidebar.y + 60, sidebar.width - 20, sidebar.height - 144)
        self.sentence_list.draw(self.screen, self.fonts, self.results, self.selected)

    # aba de derivação: árvore e passos em cima, botões de controle embaixo
    def draw_derivation_tab(self, content):

        area = pygame.Rect(content.x, content.y, content.width, content.height - CONTROLS_HEIGHT)
        views.draw_derivation(self.screen, area, self.fonts, self.result, self.step)

        # botões ficam desabilitados quando a sentença é rejeitada (não tem passos)
        controls = pygame.Rect(content.x, area.bottom + 10, content.width, CONTROLS_HEIGHT - 10)
        enabled = self.result['accepted']

        # o botão do meio troca o texto conforme está reproduzindo ou não
        self.control_buttons[2].label = 'Pausar' if self.playing else 'Reproduzir'
        x = controls.x
        for button in self.control_buttons:
            button.rect = pygame.Rect(x, controls.y, 112, controls.height)
            button.enabled = enabled
            button.draw(self.screen, self.fonts['body'])
            x += 120

        # contador de passos
        if enabled:
            counter = f'Passo {self.step} de {self.step_count() - 1}'
            views.draw_text(self.screen, self.fonts['subtitle'], counter, (x + 12, controls.centery), anchor='midleft')
