from config_supabase import config_supabase

supabase = config_supabase()

def criar_cliente_base(user_id):
    
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