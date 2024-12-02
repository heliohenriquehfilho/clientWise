import random

def gerar_numero_ean13():
    numero_aleatorio = ''.join(str(random.randint(0,9)) for _ in range(12))
    return numero_aleatorio