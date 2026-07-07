"""
Notificador WhatsApp via CallMeBot (https://www.callmebot.com) — API gratuita
para envio de mensagens ao PRÓPRIO número do usuário (uso pessoal).

Setup (uma única vez, pelo celular do usuário):
  1. Adicionar o contato +34 611 04 87 48 no telefone.
  2. Enviar por WhatsApp para esse contato: "I allow callmebot to send me messages"
  3. O bot responde com a APIKEY.
  4. Configurar no .env da VPS:
       CALLMEBOT_PHONE=+55XXXXXXXXXXX   (número com código do país)
       CALLMEBOT_APIKEY=XXXXXX

Sem as duas variáveis configuradas, send_whatsapp é no-op silencioso (retorna
False) — nada quebra.
"""
import os
import logging
import urllib.parse

import requests

logger = logging.getLogger(__name__)

CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"


def whatsapp_configured() -> bool:
    return bool(os.getenv("CALLMEBOT_PHONE") and os.getenv("CALLMEBOT_APIKEY"))


def send_whatsapp(message: str) -> bool:
    """Envia mensagem WhatsApp para o número configurado. Nunca levanta exceção."""
    phone = os.getenv("CALLMEBOT_PHONE")
    apikey = os.getenv("CALLMEBOT_APIKEY")
    if not phone or not apikey:
        logger.info("WhatsApp não configurado (CALLMEBOT_PHONE/CALLMEBOT_APIKEY ausentes) — notificação ignorada.")
        return False

    try:
        # CallMeBot limita tamanho; corta com sufixo para não perder o aviso
        if len(message) > 1500:
            message = message[:1480] + "\n(...)"
        resp = requests.get(CALLMEBOT_URL, params={
            "phone": phone,
            "text": message,
            "apikey": apikey,
        }, timeout=15)
        ok = resp.status_code == 200 and "ERROR" not in resp.text.upper()
        if ok:
            logger.info("Notificação WhatsApp enviada.")
        else:
            logger.warning(f"CallMeBot retornou {resp.status_code}: {resp.text[:200]}")
        return ok
    except Exception as e:
        logger.warning(f"Falha ao enviar WhatsApp (não-fatal): {e}")
        return False


def format_ads_recommendations_summary(summary: dict) -> str:
    """Formata o resumo diário do motor de decisão de Ads para WhatsApp."""
    created = summary.get("created", [])
    lines = [f"🤖 HyperAI — Ads: {len(created)} nova(s) recomendação(ões)"]

    action_labels = {
        "pausar": "⏸️ Pausar",
        "reduzir_ou_pausar": "📉 Reduzir/Pausar",
        "aumentar": "🚀 Aumentar",
    }
    for c in created[:8]:
        title = (c.get("title") or c.get("item_id") or "?")
        if len(title) > 45:
            title = title[:42] + "..."
        line = f"{action_labels.get(c['action_code'], c['action_code'])}: {title}"
        if c.get("impact"):
            line += f" ({c['impact']})"
        lines.append(line)
    if len(created) > 8:
        lines.append(f"...e mais {len(created) - 8}.")

    lines.append("Decidir: ia.hypershopcomercio.com.br/ads-intelligence")
    return "\n".join(lines)
