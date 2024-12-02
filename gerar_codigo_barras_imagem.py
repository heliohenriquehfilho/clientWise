import barcode
from barcode.writer import ImageWriter

def codigo_barras_imagem(numero, nome):
    barcode_format = barcode.get_barcode_class('upc')
    codigo_produto = barcode_format(numero, writer=ImageWriter())
    codigo_produto.save(f"generated_barcode_{nome}_{numero}")