from flask import Flask
import threading
import time
import requests
from bs4 import BeautifulSoup
import os
import json

# === CONFIGURAÇÕES ===
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL")  # webhook do Discord via Environment
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

    fields = []

    if removidos:
        removidos_txt = "\n".join(removidos).strip()
        if removidos_txt:
            fields.append({
                "name": "❌ Removidos",
                "value": removidos_txt,
                "inline": False
            })

    if adicionados:
        adicionados_txt = "\n".join(adicionados).strip()
        if adicionados_txt:
            fields.append({
                "name": "✅ Adicionados",
                "value": adicionados_txt,
                "inline": False
            })

    if not fields:
        print("⚠️ Alterações vazias. Nenhuma notificação será enviada.")
        return

    embed = {
        "title": "📢 ALTERAÇÃO NA GUILD DETECTADA",
        "description": "Algum noob mudou de nick na guild Cw Bagda!",
        "color": 0x00ff00,
        "fields": fields,
        "footer": {"text": "💩 NOOBS MEDROSOS"}
    }

    payload = {"embeds": [embed]}

    try:
        resp = requests.post(DISCORD_WEBHOOK, json=payload)
        if resp.status_code not in [200, 204]:
            print(f"[ERRO] Webhook falhou com status {resp.status_code}")
            print(f"[RESPOSTA] {resp.text}")
        else:
            print("[OK] Notificação enviada ao Discord.")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar notificação ao Discord: {e}")

def load_last_members():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    else:
        return []

def save_last_members(members):
    with open(STATE_FILE, "w") as f:
        json.dump(members, f)

def monitor():
    last_members = load_last_members()

    while True:
        print("🔍 Verificando membros da guild...")
        current_members = get_guild_members()

        if current_members:
            if current_members != last_members:
                send_discord_notification(last_members, current_members)
                save_last_members(current_members)
            else:
                print("✅ Nenhuma mudança detectada.")
        else:
            print("⚠️ Nenhum membro encontrado ou erro na leitura.")

        print(f"⏳ Aguardando {CHECK_INTERVAL} segundos...\n")
        time.sleep(CHECK_INTERVAL)

# === EXECUÇÃO ===
if __name__ == "__main__":
    t = threading.Thread(target=monitor)
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port=8080)
