
content = """MELI_USER_ID=511447456558343
MELI_APP_ID=2511447456558343
MELI_CLIENT_SECRET=aNGcuTD1lwWBnAzT1pL1h7SA659L2VD8
MELI_REDIRECT_URI=https://plenty-friends-sin.loca.lt/auth/ml/callback
DATABASE_URL=postgresql://postgres:gWh28%40dGcMp@localhost:5432/hypershop
"""
with open(".env", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated .env to localtunnel URI.")
