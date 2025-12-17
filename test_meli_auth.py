import os
import requests
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

def test_meli_auth():
    print("--- Teste de Autenticação Mercado Livre ---")

    # 1. Ler variáveis de ambiente
    app_id = os.getenv("MELI_APP_ID")
    client_secret = os.getenv("MELI_CLIENT_SECRET")
    redirect_uri = os.getenv("MELI_REDIRECT_URI")
    auth_code = os.getenv("MELI_AUTH_CODE")

    # 2. Validar variáveis
    missing_vars = []
    if not app_id: missing_vars.append("MELI_APP_ID")
    if not client_secret: missing_vars.append("MELI_CLIENT_SECRET")
    if not redirect_uri: missing_vars.append("MELI_REDIRECT_URI")
    if not auth_code: missing_vars.append("MELI_AUTH_CODE")

    if missing_vars:
        print(f"ERRO: Variáveis de ambiente ausentes: {', '.join(missing_vars)}")
        print("Por favor, configure-as no arquivo .env antes de executar este teste.")
        return

    # 3. Trocar Code por Token (POST /oauth/token)
    token_url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": app_id,
        "client_secret": client_secret,
        "code": auth_code,
        "redirect_uri": redirect_uri
    }

    print(f"\nTentando trocar AUTH_CODE por Access Token...")
    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status() # Lança erro para status 4xx/5xx
        
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        print("\n--- SUCESSO NA AUTENTICAÇÃO ---")
        print(f"Access Token: {access_token}")
        print(f"Refresh Token: {token_data.get('refresh_token')}")
        print(f"User ID: {token_data.get('user_id')}")
        print(f"Expires In: {token_data.get('expires_in')} segundos")

        # 4. Testar Token (GET /users/me)
        if access_token:
            print("\nTestando Access Token (GET /users/me)...")
            me_url = "https://api.mercadolibre.com/users/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            me_response = requests.get(me_url, headers=headers)
            me_response.raise_for_status()
            
            me_data = me_response.json()
            print("\n--- DADOS DO USUÁRIO ---")
            print(f"ID: {me_data.get('id')}")
            print(f"Nickname: {me_data.get('nickname')}")
            print(f"Nome completo: {me_data.get('first_name')} {me_data.get('last_name')}")
            print(f"Email: {me_data.get('email')}")
            
    except requests.exceptions.HTTPError as err:
        print("\n--- ERRO NA REQUISIÇÃO ---")
        print(f"Status Code: {err.response.status_code}")
        try:
            print(f"Detalhes: {err.response.json()}")
        except:
            print(f"Conteúdo: {err.response.text}")
    except Exception as e:
        print(f"\n--- ERRO INESPERADO ---")
        print(str(e))

if __name__ == "__main__":
    test_meli_auth()
