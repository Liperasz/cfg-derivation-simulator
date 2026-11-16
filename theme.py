import pygame

WINDOW_SIZE = (1280, 760)
MIN_WINDOW_SIZE = (960, 600)
FPS = 60
STEP_INTERVAL = 0.9  # segundos entre passos no modo reprodução

HEADER_HEIGHT = 64
SIDEBAR_WIDTH = 270
PADDING = 16
CONTROLS_HEIGHT = 56

# paleta clara, parecida com os desenhos do relatório
COLORS = {
    'background': (244, 245, 247),
    'panel': (255, 255, 255),
    'border': (215, 219, 226),
    'text': (31, 35, 40),
    'muted': (101, 109, 118),
    'accent': (37, 99, 235),
    'accent_soft': (219, 234, 254),
    'accept': (22, 163, 74),
    'accept_soft': (220, 252, 231),
    'reject': (220, 38, 38),
    'reject_soft': (254, 226, 226),
    'highlight': (253, 230, 138),
    'node': (255, 255, 255),
    'node_done': (229, 231, 235),
    'terminal': (219, 234, 254),
    'edge': (75, 85, 99),
    'button': (255, 255, 255),
    'button_hover': (238, 242, 255),
    'button_disabled': (241, 243, 245)
}

# fontes que têm ε, → e ⇒ (a padrão do pygame não tem)
FONT_CANDIDATES = ['dejavusans', 'notosans', 'segoeui', 'arial', 'liberationsans']
MONO_CANDIDATES = ['dejavusansmono', 'notosansmono', 'consolas', 'liberationmono']


# carrega as fontes usadas na interface em cada tamanho
def load_fonts():

    regular = _first_available(FONT_CANDIDATES)
    mono = _first_available(MONO_CANDIDATES) or regular

    def make(name, size, bold=False):
        return pygame.font.SysFont(name, size, bold=bold) if name else pygame.font.Font(None, size + 6)

    return {
        'title': make(regular, 22, bold=True),
        'subtitle': make(regular, 16, bold=True),
        'body': make(regular, 15),
        'small': make(regular, 13),
        'rule': make(mono, 18),
        'step': make(regular, 18),
        'language': make(regular, 18),
        'form': make(regular, 22, bold=True),
        'node': make(regular, 18, bold=True)
    }


def _first_available(candidates):
    return next((name for name in candidates if pygame.font.match_font(name)), None)
