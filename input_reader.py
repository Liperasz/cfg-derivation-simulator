from grammar import EPSILON

SECTIONS = {
    '[aceitar]': True,
    '[rejeitar]': False
}


# lê o arquivo de sentenças e devolve [(sentença, esperado)]
# esperado é True para aceitar, False para rejeitar e None se vier fora das seções
def read_sentences(path):

    sentences = []
    expected = None

    with open(path, 'r', encoding='utf-8') as input_file:
        for line in input_file:

            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # cabeçalho de seção muda o resultado esperado das próximas linhas
            if line.lower() in SECTIONS:
                expected = SECTIONS[line.lower()]
                continue

            word = '' if line == EPSILON else line
            sentences.append((word, expected))

    return sentences
