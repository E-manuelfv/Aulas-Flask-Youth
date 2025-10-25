import secrets

# Opção 1: Usando secrets.token_hex() (Recomendado para facilidade de uso)
# Gera uma string hexadecimal com 32 bytes (64 caracteres)
secret_key_hex = secrets.token_hex(32)

print(f"Chave Secreta (Hex): {secret_key_hex}")