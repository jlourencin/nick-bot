from flask import Flask
import threading
import time
import requests
from bs4 import BeautifulSoup
import os
import json

# === CONFIGURAÇÕES ===
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")  # variáveis devem ser configuradas no Railway
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
            "title": "📢 ATENÇÃO! ALTERAÇÃO NA GUILD DETECTADA",
            "description": "Algum personagem foi removido ou entrou na guild!",
            "color": 0x3498db,
            "fields": [],
