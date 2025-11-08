# Importe sua variável global 'supabase' configurada no Factory
from app.models.supabase_client import supabase 

# Nome da sua tabela de produtos no Supabase
PRODUCTS_TABLE = 'produtos' 

def get_all_products():
    """Busca todos os produtos da tabela 'products'."""
    try:
        # Foco na Query: .select('*') -> SELECT * FROM products
        response = supabase.table(PRODUCTS_TABLE).select('*').execute()
        
        # O response contém dados, status, etc.
        # Retornamos o objeto completo para a Rota decidir o que fazer.
        return response
    except Exception as e:
        print(f"Erro ao buscar produtos no Supabase: {e}")
        # Retorna um objeto vazio ou um erro
        return None