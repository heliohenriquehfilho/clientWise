from config_supabase import config_supabase

supabase = config_supabase()

def cliente_base(user_id):
    
    cliente = {
        "nome": "Cliente Exemplo",
        "contato": "+55 (48) 99999-9999",
        "email": "exemplo@cliente.com",
        "endereco": "Rua Exemplo, 123",
        "bairro": "Centro",
        "cidade": "Florianópolis",
        "estado": "Santa Catarina",
        "cep": "12345-678",
        "ativo": True,
        "genero": "Não Binário",
        "idade": 25,
        "user_id": user_id
    }

    supabase.table("clientes").insert(cliente).execute()

def vendas_base(user_id):
    
    venda = {	
        "cliente": "Cliente Exemplo",
        'produto': 'Produto Exemplo',	
        'quantidade': 1,
        "desconto": 0,
        "data_venda": "2024-01-01",
        "pagamento": "Pix",
        "vendedor": "Vendedor Exemplo",
        "user_id": user_id,
        "valor": 20,
    }

    supabase.table("vendas").insert(venda).execute()

def produtos_base(user_id):
    
    produto = {	
        'nome': "Produto Exemplo",
        'preco': 29.90,
        'descricao': "Produto de Exemplo para Novos Usuários",
        'quantidade': 2,
        'ativo': True,
        'codigo_barras': "",
        'custo': 9.90,
        'margem_lucro': ((29.90 - 9.90) / 9.90),
        'user_id': user_id,
        'tipo': "Fisico"
    }

    supabase.table("produtos").insert(produto).execute()

def vendedor_base(user_id):
    
    vendedor = {		
        'nome': "Vendedor Exemplo",
        'telefone': "55 (11) 99999-0999",
        'email': "vendedor@exemplo.com",
        'idade': 0,
        "contratacao": "2024-01-01",
        'demissao': "2025-01-02",
        "salario": 1500.00,
        "encargos": 5226,
        "user_id": user_id,
        "aumentos": [{"Data": "2024-12-01", "Valor": 250.0}]
    }

    supabase.table("vendedores").insert(vendedor).execute()