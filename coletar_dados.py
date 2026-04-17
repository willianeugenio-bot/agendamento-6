import requests
import json
import os
from datetime import datetime, timedelta, timezone

# URIs dos novos assessores da equipe "Vida com CNPJ"
URIs = [
    "https://api.calendly.com/event_types/b6c20223-aeb2-4777-908f-3bb5a6aa998e"
]

# Mapeamento (As cores não aparecerão na tela final, mas mantemos por estrutura)
MAPA_NOMES = {
    "b6c20223-aeb2-4777-908f-3bb5a6aa998e": {"nome": "Maria Luiza", "cor": "#007bff"}
}

TOKEN = os.getenv("CALENDLY_TOKEN")
headers = {"Authorization": f"Bearer {TOKEN}"}

def obter_horarios():
    eventos_final = []
    agora_utc = datetime.now(timezone.utc)

    for uri in URIs:
        uuid = uri.split('/')[-1]
        info = MAPA_NOMES.get(uuid)
        
        if not info:
            continue # Pula se o UUID não estiver no mapa
            
        # Dividimos em duas buscas para respeitar o limite de 7 dias do Calendly
        # Fatias: [Hoje até dia 7] e [Dia 7 até dia 10]
        intervalos = [
            (agora_utc + timedelta(minutes=1), agora_utc + timedelta(days=7)),
            (agora_utc + timedelta(days=7, minutes=1), agora_utc + timedelta(days=15))
        ]
        
        for start_time, end_time in intervalos:
            params = {
                "event_type": uri,
                "start_time": start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "end_time": end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            
            try:
                res = requests.get("https://api.calendly.com/event_type_available_times", headers=headers, params=params)
                if res.status_code == 200:
                    slots = res.json().get('collection', [])
                    for slot in slots:
                        eventos_final.append({
                            "title": f"Falar com {info['nome']}",
                            "start": slot['start_time'],
                            "url": slot['scheduling_url']
                        })
            except Exception as e:
                print(f"Erro ao processar {info['nome']}: {e}")

    with open("horarios.json", "w") as f:
        json.dump(eventos_final, f, indent=4)
    print("Arquivo horarios.json atualizado com sucesso (10 dias buscados).")

if __name__ == "__main__":
    obter_horarios()
