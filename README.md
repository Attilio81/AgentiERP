# AgentiERP - Multi-Agent Chat System

Sistema di chat AI multi-agente per interrogare database SQL Server tramite linguaggio naturale.

Permette a utenti business di porre domande in italiano su **magazzino**, **ordini** e **vendite**, ottenendo risposte basate su query SQL sicure eseguite su SQL Server.

---

## 🎯 Caratteristiche principali

- **Agenti specializzati**: `magazzino`, `ordini`, `vendite`, ognuno con il proprio prompt e set di tool SQL.
- **Streaming in tempo reale**: le risposte vengono mostrate mentre l'AI le genera.
- **Autenticazione a sessione**: registrazione/login, sessioni con scadenza, password hashate.
- **Query SQL sicure**: solo `SELECT`, validazione per bloccare comandi distruttivi.
- **Cronologia conversazioni**: conversazioni e messaggi salvati nello schema `chat_ai`.
- **Conversazioni recenti filtrate per agente**: la lista mostra solo le domande dell'agente selezionato.
- **FAQ suggerite per agente**: lista di domande frequenti generate da un modello più leggero dedicato alle FAQ.
- **Pannello Admin Agenti**: gestione descrizione, system prompt, modello e tools degli agenti direttamente da UI.

---

## 🏗️ Architettura

```text
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Streamlit  │────▶│   FastAPI    │────▶│ SQL Server  │
│  Frontend   │◀────│   Backend    │◀────│  Database   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Datapizza   │
                    │   Agents     │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Claude     │
                    │   (Anthropic)│
                    └──────────────┘
```

---

## 🧰 Stack tecnologico

- **Backend**: FastAPI, SQLAlchemy, Datapizza-AI, Anthropic SDK, Pydantic Settings.
- **Frontend**: Streamlit + `requests`.
- **Database**: SQL Server (schema applicativo `chat_ai` + schemi di dominio `magazzino`, `ordini`, `vendite`).
- **Autenticazione**: session-based, password hashate con `passlib[bcrypt]`.
- **AI**:
  - Modello principale: `AGENT_MODEL` (es. Claude Sonnet).
  - Modello FAQ: `FAQ_MODEL` (es. Claude Haiku) per generare domande frequenti leggere.

---

## 📂 Repository GitHub

Repository ospitato su GitHub:

- URL: `https://github.com/Attilio81/AgentiERP`

Per clonare il progetto:

```powershell
git clone https://github.com/Attilio81/AgentiERP.git
cd AgentiERP
```

---

## 📁 Struttura del progetto

```text
AgentiERP/
├── backend/
│   ├── app/
│   │   ├── agents/           # Sistema agenti Datapizza
│   │   │   ├── manager.py    # Inizializzazione e registry degli agenti
│   │   │   ├── prompts.py    # Prompt di sistema per i diversi agenti
│   │   │   └── sql_tools.py  # Tool SQL esposti agli agenti
│   │   ├── admin/            # API pannello amministrazione agenti
│   │   │   └── routes.py
│   │   ├── auth/             # Autenticazione e sessioni
│   │   │   ├── routes.py
│   │   │   ├── session.py
│   │   │   └── middleware.py
│   │   ├── chat/             # Endpoints di chat e conversazioni
│   │   │   └── routes.py
│   │   ├── database/         # Connessione e modelli SQLAlchemy
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   └── init_schema.sql
│   │   ├── config.py         # Configurazione (Settings)
│   │   └── main.py           # Entry point FastAPI
│   ├── requirements.txt
│   ├── test_setup.py         # Test rapido di setup
│   └── test_retry_logic.py   # Test logica di retry Anthropic
├── frontend/
│   ├── app.py                # UI Streamlit
│   └── requirements.txt
├── QUICKSTART.md             # Guida rapida
├── STATUS.md                 # Stato sistema e note compatibilità
├── TROUBLESHOOTING.md        # Problemi comuni
├── docker-compose.yml        # Bozza per deploy Docker
├── .env.example              # Esempio configurazione ambiente
└── README.md                 # Questo file
```

---

## 📋 Prerequisiti

1. **Python 3.11+**  
   Testato e funzionante anche con **Python 3.13** (vedi `STATUS.md` per dettagli).
2. **SQL Server** accessibile dalla macchina che esegue il backend.
3. **ODBC Driver 18 for SQL Server** installato.
4. **Chiave API Anthropic** valida (Claude).
5. Sistema operativo: ambiente Windows con PowerShell (comandi negli esempi).

---

## ⚙️ Configurazione ambiente (`.env`)

Parti dalla root del progetto (cartella che contiene questo `README.md`):

```powershell
copy .env.example .env
copy .env backend\.env   # pydantic-settings legge .env dalla cartella backend
```

Apri `.env` e imposta i valori principali:

```env
DATABASE_URL=mssql+pyodbc://user:password@server:1433/database?driver=ODBC+Driver+18+for+SQL+Server
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

SECRET_KEY=your-secret-key-here-minimum-32-characters
SESSION_EXPIRE_HOURS=24

AGENT_MODEL=claude-sonnet-4-5-20250929
FAQ_MODEL=claude-haiku-4-5-20250929

BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:8501
```

Per generare una `SECRET_KEY` sicura:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

> ℹ️ In produzione assicurati di **non committare** il file `.env` e di usare variabili d'ambiente sicure.

---

## 🗄️ Inizializzazione database

Lo schema applicativo `chat_ai` (utenti, sessioni, conversazioni, messaggi, configurazione agenti) viene creato tramite `init_schema.sql`.

### Opzione A – `sqlcmd`

```powershell
sqlcmd -S your_server -d your_database -U your_user -P your_password -i backend\app\database\init_schema.sql
```

### Opzione B – SQL Server Management Studio (SSMS)

1. Apri `backend/app/database/init_schema.sql` in SSMS.
2. Modifica la riga `USE [YourDatabaseName];` con il nome del tuo database.
3. Esegui lo script.

> Assicurati che il database contenga anche gli schemi di dominio (`magazzino`, `ordini`, `vendite`) o adatta `prompts.py` e `sql_tools.py` ai tuoi schemi.

---

## 📦 Installazione dipendenze

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Frontend

```powershell
cd ..\frontend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
```

### Verifica setup

Dalla root del progetto:

```powershell
python test_setup.py
```

Se vedi `🎉 All tests passed!` il setup base è corretto.

---

## ▶️ Avvio in sviluppo

### Terminal 1 – Backend FastAPI

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Endpoint utili:

- API Docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

### Terminal 2 – Frontend Streamlit

```powershell
cd frontend
.\venv\Scripts\Activate.ps1
streamlit run app.py
```

Frontend disponibile su `http://localhost:8501`.

Per fermare i servizi: `Ctrl + C` nei rispettivi terminali.

---

## 💡 Utilizzo dell'applicazione

1. Apri `http://localhost:8501` nel browser.
2. Nella pagina di login/registrazione:
   - Registra un nuovo utente (tab **Registrazione**).
   - Effettua il **login**.
3. Dalla **sidebar**:
   - Seleziona un **agente**: `magazzino`, `ordini` o `vendite`.
   - Avvia una **nuova conversazione** o seleziona una conversazione recente.
4. Scrivi la tua domanda in linguaggio naturale nel campo chat.

### Conversazioni recenti (filtrate per agente)

Nella sidebar:

- La sezione **"Conversazioni recenti"** mostra le ultime domande, **solo per l'agente attualmente selezionato**.
- Cambiando agente, l'elenco viene aggiornato automaticamente per mostrare solo le conversazioni legate a quell'agente.

### FAQ suggerite per agente

Sempre in sidebar, sotto le conversazioni recenti:

- Sezione **"FAQ suggerite"**:
  - Usa le ultime domande effettuate per l'agente corrente.
  - Chiama un endpoint backend `/api/chat/faq_suggestions` che a sua volta usa un modello Anthropic leggero (`FAQ_MODEL`).
  - Genera una lista di domande "pronte all'uso" (senza placeholder), pulite e normalizzate.
- Puoi:
  - Premere **"Genera/aggiorna FAQ"** per rigenerare le proposte.
  - Espandere ogni FAQ per leggere l'eventuale risposta di esempio.
  - Cliccare **"Usa questa FAQ"** per precompilare la chat con quella domanda e rilanciarla come nuova richiesta.

### Pannello Admin Agenti

Se l'utente autenticato è `admin`:

- Nella sidebar appare il **"Pannello Admin Agenti"**.
- Permette di:
  - Selezionare un agente.
  - Modificare **descrizione**, **system prompt**, **modello** e **tool_names**.
  - Attivare/disattivare un agente.
- Alla conferma, l'`AgentManager` viene reinizializzato per applicare subito le modifiche.

---

## 🔌 API principali

### Autenticazione (`/api/auth`)

- `POST /api/auth/register` – Registrazione utente.
- `POST /api/auth/login` – Login, restituisce `session_id`.

Tutte le API protette richiedono l'header:

```http
X-Session-ID: <session_id>
```

### Chat (`/api/chat`)

- `GET /api/chat/agents` – Lista agenti disponibili (nome + descrizione).
- `POST /api/chat/stream` – Endpoint principale di chat (SSE):
  - Body: `{ "agent_name", "message", "conversation_id"? }`.
  - Salva messaggi e aggiorna `conversation_id`.
- `GET /api/chat/conversations` – Lista conversazioni dell'utente (più recenti prima).
- `GET /api/chat/conversations/{id}/messages` – Messaggi di una conversazione.
- `GET /api/chat/faq_suggestions` – FAQ suggerite per agente corrente:
  - Query string: `agent_name`, `limit`.
  - Restituisce una lista di `{ "question", "answer" }`.

### Admin (`/api/admin`)

- `GET /api/admin/agents` – Lista completa configurazioni agenti.
- `PUT /api/admin/agents/{agent_id}` – Aggiornamento configurazione agente.

---

## 🧪 Test e strumenti di debug

- `backend/test_setup.py` – Verifica rapida di connessione DB e configurazione base.
- `backend/test_retry_logic.py` – Testa la logica di retry per errori 529 (Overloaded) di Anthropic.
- `backend/inspect_agent.py` – Script di ispezione per le classi `Agent`, `AnthropicClient`, `StepResult` di Datapizza-AI.

Esecuzione esempio:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python test_retry_logic.py
```

---

## 🐛 Troubleshooting rapido

Per una lista più completa vedi `QUICKSTART.md` e `TROUBLESHOOTING.md`. Alcuni casi comuni:

### Backend non si avvia

- Verifica virtualenv attivo e dipendenze installate.
- Controlla `backend/.env` (DATABASE_URL, ANTHROPIC_API_KEY, SECRET_KEY).
- Verifica che SQL Server sia raggiungibile.

### Errore connessione database

- Controlla `DATABASE_URL` in `.env`.
- Verifica che **ODBC Driver 18** sia installato.
- Testa con `sqlcmd` da terminale.

### Frontend non comunica con backend

- Backend deve essere in esecuzione su `http://localhost:8000`.
- Verifica CORS in `backend/app/main.py`.

### Problemi con Python 3.13

- Vedi `STATUS.md` e `TROUBLESHOOTING.md` per note su compatibilità e versioni pacchetti.

---

## 📝 Roadmap / Miglioramenti futuri

- [ ] Completare configurazione Docker/Docker Compose per deploy.
- [ ] Aggiungere test unitari e di integrazione.
- [ ] Logging strutturato e centralizzato.
- [ ] Metriche e monitoring (es. Prometheus + Grafana).
- [ ] Cache delle query frequenti.
- [ ] Export conversazioni e log.
- [ ] Grafici e visualizzazioni dati più ricchi.
- [ ] Supporto a più database / schemi personalizzati.

---

## 📄 Licenza

Progetto interno – Tutti i diritti riservati.

---

## 👥 Supporto

Per problemi o domande:

- consulta `QUICKSTART.md`, `STATUS.md` e `TROUBLESHOOTING.md`;
- contatta il team di sviluppo interno.
