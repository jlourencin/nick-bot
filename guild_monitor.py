from flask import Flask
import threading
import time
import requests
from bs4 import BeautifulSoup
import os
import json

# === CONFIGURAÇÕES ===
DISCORD_WEBHOOK = os.environ.get("https://discord.com/api/webhooks/1399578365073297418/KziH0IYXYPvG0hIv0itHYjutg_D_mHvL_3zflD4lasdnw3lOwgZJmjJajeI9HeJx0d6E)  # webhook do Discord
CHECK_INTERVAL = 60  # segundos
STATE_FILE = "last_members.json"
GUILD_URL = "https://bleachgame.online/?guilds/Cw+Bagda"

# === SERVIDOR FLASK ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot de monitoramento de guild rodando!", 200

# === FUNÇÕES ===

def get_guild_members():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(GUILD_URL, headers=headers, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"[ERRO] Falha ao acessar a guild: {e}")
        return []

    soup = BeautifulSoup(r.text, 'html.parser')
    members = []

    for row in soup.select("tr"):
        cols = row.find_all("td")
        if len(cols) >= 2:
            name = cols[0].text.strip()
            if name:
                members.append(name)
    return members

def send_discord_notification(old_list, new_list):
    old_set = set(old_list)
    new_set = set(new_list)

    removidos = old_set - new_set
    adicionados = new_set - old_set

    if removidos or adicionados:
        embed = {
            "title": "📢 ATENÇÃO! ALGUM NOOB MUDOU O NICK",
            "description": "NÃO ADIANTA CORRER, VAMOS CONTINUAR OPRIMINDO VOCÊ, SEU NOOBZINHO",
            "color": 0x3498db,
            "fields": [],
            "footer": {"text": "💩 NOOBS MEDROSOS"}
        }

        if removidos:
            embed["fields"].append({
                "name": "❌ Removidos",
                "value": "\n".join(removidos),
                "inline": False
            })

        if adicionados:
            embed["fields"].append({
                "name": "✅ Adicionados",
                "value": "\n".join(adicionados),
                "inline": False
            })

        payload = {"embeds": [embed]}
        try:
            resp = requests.post(DISCORD_WEBHOOK, json=payload)
            if resp.status_code not_
