import pygame

from ui.theme import COLORS

RADIUS = 8


# botão simples: guarda o retângulo e a ação, o App chama click() nos eventos
class Button:

    def __init__(self, label, action, rect=None, enabled=True, active=False):

        self.label = label
        self.action = action
        self.rect = pygame.Rect(rect) if rect else pygame.Rect(0, 0, 0, 0)
        self.enabled = enabled
        self.active = active

    def draw(self, surface, font):

        hover = self.enabled and self.rect.collidepoint(pygame.mouse.get_pos())

        # aba ativa fica preenchida com a cor de destaque
        if self.active:
            background, text_color, border = COLORS['accent'], COLORS['panel'], COLORS['accent']
        elif not self.enabled:
            background, text_color, border = COLORS['button_disabled'], COLORS['muted'], COLORS['border']
        else:
            background = COLORS['button_hover'] if hover else COLORS['button']
            text_color, border = COLORS['text'], COLORS['border']

        # fundo, borda e o texto centralizado
        pygame.draw.rect(surface, background, self.rect, border_radius=RADIUS)
        pygame.draw.rect(surface, border, self.rect, width=1, border_radius=RADIUS)

        label = font.render(self.label, True, text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))

    # executa a ação se o clique foi dentro do botão, e avisa se tratou o clique
    def click(self, position):

        if self.enabled and self.rect.collidepoint(position):
            self.action()
            return True

        return False


# lista lateral das sentenças, com rolagem quando não cabe
class SentenceList:

    ITEM_HEIGHT = 58

    def __init__(self, on_select):

        self.on_select = on_select
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.scroll = 0

    def draw(self, surface, fonts, results, selected):

        # limita o desenho à área da lista, pra item rolado não invadir o resto da lateral
        previous_clip = surface.get_clip()
        surface.set_clip(self.rect)

        for index, result in enumerate(results):

            # pula os itens que estão fora da área visível
            item = self._item_rect(index)
            if item.bottom < self.rect.top or item.top > self.rect.bottom:
                continue

            # item selecionado ganha fundo azul claro
            is_selected = index == selected
            background = COLORS['accent_soft'] if is_selected else COLORS['panel']
            border = COLORS['accent'] if is_selected else COLORS['border']
            # borda vermelha quando o obtido não bate com o esperado
            if not result['matches']:
                border = COLORS['reject']

            pygame.draw.rect(surface, background, item, border_radius=RADIUS)
            pygame.draw.rect(surface, border, item, width=2 if is_selected else 1, border_radius=RADIUS)

            # sentença em cima e o resultado esperado embaixo
            word = fonts['rule'].render(result['word'] or 'ε', True, COLORS['text'])
            surface.blit(word, (item.x + 12, item.y + 8))

            expected = {True: 'esperado: aceitar', False: 'esperado: rejeitar', None: 'sem resultado esperado'}
            caption = fonts['small'].render(expected[result['expected']], True, COLORS['muted'])
            surface.blit(caption, (item.x + 12, item.y + 34))

            self._draw_badge(surface, fonts, item, result['accepted'])

        surface.set_clip(previous_clip)

    # selo com o resultado obtido no canto direito do item
    def _draw_badge(self, surface, fonts, item, accepted):

        text = 'ACEITA' if accepted else 'REJEITA'
        color = COLORS['accept'] if accepted else COLORS['reject']
        soft = COLORS['accept_soft'] if accepted else COLORS['reject_soft']

        label = fonts['small'].render(text, True, color)
        badge = label.get_rect().inflate(14, 8)
        badge.midright = (item.right - 10, item.centery)

        pygame.draw.rect(surface, soft, badge, border_radius=RADIUS)
        surface.blit(label, label.get_rect(center=badge.center))

    # posição do item na tela, já descontando a rolagem
    def _item_rect(self, index):
        top = self.rect.y + index * (self.ITEM_HEIGHT + 8) - self.scroll
        return pygame.Rect(self.rect.x, top, self.rect.width, self.ITEM_HEIGHT)

    # descobre qual item foi clicado e avisa o App
    def click(self, position, count):

        if not self.rect.collidepoint(position):
            return False

        for index in range(count):
            if self._item_rect(index).collidepoint(position):
                self.on_select(index)
                return True

        return False

    # rola a lista sem passar do começo nem do fim do conteúdo
    def wheel(self, amount, count):
        content_height = count * (self.ITEM_HEIGHT + 8)
        max_scroll = max(0, content_height - self.rect.height)
        self.scroll = min(max(self.scroll - amount * 30, 0), max_scroll)

    # rola o mínimo necessário pra deixar o item selecionado à vista
    def ensure_visible(self, index):

        item = self._item_rect(index)
        if item.top < self.rect.top:
            self.scroll -= self.rect.top - item.top
        elif item.bottom > self.rect.bottom:
            self.scroll += item.bottom - self.rect.bottom
