from app.models.supabase_client import supabase 

PRODUCTS_TABLE = 'produtos'

def get_all_products():
    try:
        response = supabase.table(PRODUCTS_TABLE).select('*').execute()
        return response
    except Exception as e:
        print(f"Erro ao buscar produtos: {e}")
        return None