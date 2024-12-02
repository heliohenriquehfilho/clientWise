import os
import json

def salvar_em_json(dados, arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, 'r') as f:
            existentes = json.load(f)
    else:
        existentes = []
    existentes.append(dados)
    with open(arquivo, "w") as f:
        json.dump(existentes, f, indent=4)