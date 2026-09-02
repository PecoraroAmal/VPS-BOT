# VPS-BOT

Bot Telegram per monitorare lo stato di una VPS: CPU, RAM, disco, rete e uptime, con comando `/status` on-demand e alert automatici quando le risorse superano soglie di warning o critiche.

## Funzionalità

- **`/status`** — restituisce uno snapshot immediato di CPU, RAM, disco, rete e uptime
- **Alert automatici** — controllo periodico in background; se una metrica supera una soglia (warning o critical) arriva una notifica con lo stato completo di tutte le metriche
- **Nessuna porta esposta** — funziona in long polling, non richiede webhook né porte aperte verso internet

## Requisiti

- Python 3.10+
- Un bot Telegram creato tramite [@BotFather](https://t.me/BotFather)

## Installazione

```bash
git clone <url-di-questo-repo>
cd VPS-BOT
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configurazione

Crea un file `.env` nella cartella del progetto (non viene incluso nel repo, va creato manualmente):

```
TELEGRAM_BOT_TOKEN=il_tuo_token_da_botfather
TELEGRAM_CHAT_ID=il_tuo_chat_id
```

Per ottenere il `chat_id`:
1. Manda un messaggio qualsiasi al tuo bot su Telegram
2. Apri nel browser: `https://api.telegram.org/bot<TUO_TOKEN>/getUpdates`
3. Cerca il campo `"chat":{"id": ...}` nella risposta JSON

Le soglie di warning/critical per CPU, RAM e disco, oltre all'intervallo di controllo, si configurano in `config.py`.

## Avvio

```bash
python3 bot.py
```

Per farlo girare permanentemente in background su un server Linux, si consiglia un servizio `systemd` con riavvio automatico in caso di crash.

## Struttura del progetto
```
VPS-BOT/
├── bot.py # logica del bot: comandi e job periodico
├── metrics.py # raccolta metriche di sistema (psutil)
├── formatter.py # formattazione dei messaggi Telegram
├── config.py # caricamento configurazione e soglie
├── requirements.txt
└── .env # NON incluso nel repo — da creare manualmente
```

## Sicurezza

Il file `.env` contiene credenziali sensibili e **non deve mai essere committato**. È già escluso tramite `.gitignore`.

## Licenza

Progetto personale, uso libero.