# AgentiERP - Multi-Agent Chat System

Sistema di chat AI multi-agente per interrogare database SQL Server tramite linguaggio naturale.

Permette a utenti business di porre domande in italiano su dati aziendali, ottenendo risposte basate su query SQL sicure eseguite su SQL Server.

---

## 🎯 Caratteristiche principali

- **Sistema agenti completamente dinamico**: Agenti configurabili via database e Admin Panel, senza modifiche al codice
- **Streaming in tempo reale**: Le risposte vengono mostrate mentre l'AI le genera
- **Autenticazione a sessione**: Registrazione/login, sessioni con scadenza, password hashate
- **Query SQL sicure**: Solo `SELECT`, validazione per bloccare comandi distruttivi
- **Cronologia conversazioni**: Conversazioni e messaggi salvati nello schema `chat_ai`
- **Conversazioni recenti filtrate per agente**: La lista mostra solo le domande dell'agente selezionato
- **FAQ suggerite per agente**: Lista di domande frequenti generate da un modello dedicato
- **Pannello Admin Agenti**: Gestione completa di descrizione, system prompt, modello e tools degli agenti direttamente da UI
- **Architettura basata su Datapizza-AI**: Framework modulare per agenti production-ready

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
                    │  LLM Client  │
                    │ (Anthropic/  │
                    │  OpenAI/Gem) │
                    └──────────────┘
```

### Flusso Dinamico degli Agenti

```text
1. Database (chat_ai.agents) → Configurazione agenti
                                ├─ name (es. "vendite")
                                ├─ description
                                ├─ system_prompt (personalizzabile)
                                ├─ tool_names (es. "sql_select")
                                ├─ model (opzionale, override AGENT_MODEL)
                                ├─ db_uri (opzionale, override DATABASE_URL)
                                └─ is_active

2. AgentManager (startup) → Carica agenti attivi da DB
                           → Crea istanze Datapizza Agent
                           → Associa tools SQL dinamicamente

3. Admin Panel (runtime) → Modifica configurazione agenti
                         → Salva su DB
                         → Reinizializza AgentManager
                         → Agenti aggiornati senza restart
```

---

## 🧰 Stack tecnologico

- **Backend**: FastAPI, SQLAlchemy, Datapizza-AI, Anthropic SDK, Pydantic Settings
- **Frontend**: Streamlit + `requests`
- **Database**: SQL Server (schema applicativo `chat_ai` + schemi di dominio personalizzati)
- **Autenticazione**: Session-based, password hashate con `passlib[bcrypt]`
- **AI**:
  - Provider selezionabile via `LLM_PROVIDER` (`anthropic`, `openai`, `gemini`)
  - Modello principale: `AGENT_MODEL` (es. Claude Sonnet 4.5 / GPT‑4.1 / Gemini 1.5 Pro)
  - Modello FAQ: `FAQ_MODEL` (es. Claude Haiku 4.5 / GPT‑4.1 mini / Gemini 1.5 Flash)
- **Retry Logic**: Gestione automatica errori 529 Overloaded di Anthropic con backoff esponenziale

---

## 🔄 Sistema Agenti Dinamico

### Configurazione Database-Driven

Gli agenti **NON sono hardcoded**. Ogni agente è una riga nella tabella `chat_ai.agents`:

| Campo | Descrizione | Esempio |
|-------|-------------|---------|
| `name` | Nome identificativo univoco | `vendite`, `magazzino`, `ordini` |
| `description` | Descrizione breve per UI | "Analisi vendite e reporting" |
| `system_prompt` | Prompt completo dell'agente | "Sei un assistente AI specializzato..." |
| `tool_names` | Tools disponibili (CSV) | `sql_select` o `sql_select,get_schema` |
| `model` | Modello AI (opzionale) | `claude-sonnet-4-5-20250929` |
| `db_uri` | Connection string DB (opzionale) | `mssql+pyodbc://...` |
| `schema_name` | Schema SQL target (opzionale) | `vendite`, `magazzino` |
| `is_active` | Agente attivo/disattivo | `1` o `0` |

### Vantaggi dell'Approccio Dinamico

✅ **Nessun deploy per modifiche agenti**: Cambi prompt via Admin Panel  
✅ **Multi-tenant ready**: Ogni agente può puntare a DB/schema diversi  
✅ **A/B testing prompt**: Duplica agente, modifica prompt, confronta risultati  
✅ **Attivazione/disattivazione runtime**: Disabilita agenti senza toccare codice  
✅ **Estensibilità**: Aggiungi nuovi agenti semplicemente inserendo righe nel DB  

### File `prompts.py`: Solo Template di Riferimento

⚠️ **IMPORTANTE**: Il file `backend/app/agents/prompts.py` contiene:
- `MAGAZZINO_PROMPT`, `ORDINI_PROMPT`, `VENDITE_PROMPT`
- Sono **template iniziali** per popolare il database
- **NON vengono usati a runtime**
- L'agente usa sempre `chat_ai.agents.system_prompt` dal database

Workflow:
1. `prompts.py` → Seed iniziale del database (`python scripts/seed_agents.py`)
2. Database `chat_ai.agents` → Fonte di verità per gli agenti
3. Admin Panel → Modifiche runtime ai prompt
4. `AgentManager` → Reinizializzazione automatica dopo modifiche

---

## 📂 Struttura del progetto

```text
AgentiERP/
├── backend/
│   ├── app/
│   │   ├── agents/           # Sistema agenti Datapizza
│   │   │   ├── manager.py    # AgentManager: carica agenti da DB
│   │   │   ├── prompts.py    # Template iniziali (non usati a runtime)
│   │   │   ├── sql_tools.py  # Tool SQL factory dinamici
│   │   │   └── client_wrapper.py  # Retry logic Anthropic
│   │   ├── admin/            # API pannello amministrazione agenti
│   │   │   └── routes.py     # CRUD agenti + reinizializzazione
│   │   ├── auth/             # Autenticazione e sessioni
│   │   │   ├── routes.py     # Login/logout/register
│   │   │   ├── session.py    # Session management
│   │   │   └── middleware.py # Auth dependencies FastAPI
│   │   ├── chat/             # Endpoints di chat e conversazioni
│   │   │   └── routes.py     # SSE streaming + FAQ generation
│   │   ├── database/         # Connessione e modelli SQLAlchemy
│   │   │   ├── database.py   # Engine e SessionLocal
│   │   │   ├── models.py     # ORM models (User, Session, Conversation, Message, AgentConfig)
│   │   │   └── init_schema.sql  # Schema SQL completo
│   │   ├── config.py         # Configurazione (Settings)
│   │   └── main.py           # Entry point FastAPI
│   ├── scripts/              # Utility scripts
│   │   └── seed_agents.py    # Popola agenti di default da prompts.py
│   ├── requirements.txt
│   ├── test_setup.py         # Test rapido di setup
│   └── test_retry_logic.py   # Test logica di retry Anthropic
├── frontend/
│   ├── app.py                # UI Streamlit con Admin Panel
│   └── requirements.txt
├── QUICKSTART.md             # Guida rapida
├── STATUS.md                 # Stato sistema e compatibilità Python 3.13
├── TROUBLESHOOTING.md        # Problemi comuni
├── SETUP_VISTE.sql           # Script esempio per creare viste SQL
├── docker-compose.yml        # Bozza per deploy Docker (TODO)
├── .env.example              # Esempio configurazione ambiente
└── README.md                 # Questo file
```

---

## 📋 Prerequisiti

1. **Python 3.10+** (testato su Python 3.11 e 3.13)
2. **SQL Server** accessibile dalla macchina che esegue il backend
3. **ODBC Driver 18 for SQL Server** installato
4. **Chiave API Anthropic** valida (Claude)
5. Sistema operativo: Windows con PowerShell (comandi negli esempi)

---

## ⚙️ Configurazione ambiente (`.env`)

Parti dalla root del progetto:

```powershell
copy .env.example .env
copy .env backend\.env   # pydantic-settings legge .env dalla cartella backend
```

Apri `.env` e imposta i valori:

```env
DATABASE_URL=mssql+pyodbc://user:password@server:1433/database?driver=ODBC+Driver+18+for+SQL+Server
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
OPENAI_API_KEY=sk-openai-your-api-key-here
GEMINI_API_KEY=sk-gemini-your-api-key-here

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

---

## 🗄️ Inizializzazione database

### Passo 1: Schema Applicativo

Lo schema `chat_ai` contiene:
- `users` - Utenti del sistema
- `sessions` - Sessioni di autenticazione
- `conversations` - Conversazioni degli utenti
- `messages` - Messaggi delle conversazioni
- **`agents`** - **Configurazione dinamica degli agenti AI**

#### Opzione A – `sqlcmd`

```powershell
sqlcmd -S your_server -d your_database -U your_user -P your_password -i backend\app\database\init_schema.sql
```

#### Opzione B – SQL Server Management Studio (SSMS)

1. Apri `backend/app/database/init_schema.sql` in SSMS
2. Modifica la riga `USE [YourDatabaseName];` con il nome del tuo database
3. Esegui lo script

### Passo 2: Agenti di Default

Dopo aver creato lo schema `chat_ai`, popola gli agenti base:

#### Opzione A – Script Python (Consigliato)

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python scripts\seed_agents.py
```

Output atteso:
```
============================================================
Seed Agenti - Multi-Agent Chat System
============================================================
✓ Creato: magazzino
✓ Creato: ordini
✓ Creato: vendite

============================================================
✓ Seed completato con successo!
============================================================

Agenti attivi nel database: 3
```

#### Opzione B – SQL Manuale

```sql
USE YourDatabase;

INSERT INTO chat_ai.agents (name, description, system_prompt, tool_names, is_active)
VALUES 
  ('magazzino', 
   'Gestione magazzino e giacenze',
   'Sei un assistente AI specializzato nella gestione del magazzino...', 
   'sql_select', 
   1),
  ('ordini', 
   'Gestione ordini clienti e fornitori',
   'Sei un assistente AI specializzato nella gestione degli ordini...', 
   'sql_select', 
   1),
  ('vendite', 
   'Analisi vendite e reporting',
   'Sei un assistante AI specializzato nell''analisi delle vendite...', 
   'sql_select', 
   1);
```

> 💡 **Tip**: Copia i prompt completi da `backend/app/agents/prompts.py`

#### Opzione C – Via Admin Panel (Post-Startup)

1. Avvia backend e frontend
2. Registrati come utente `admin`
3. Usa il "Pannello Admin Agenti" per creare agenti manualmente

### Passo 3: Schemi di Dominio (Opzionale)

Gli agenti di esempio interrogano schemi `magazzino`, `ordini`, `vendite`.

**Se i tuoi schemi hanno nomi diversi:**
1. Crea gli agenti con i nomi/schemi corretti via Admin Panel
2. Oppure modifica i system_prompt in `chat_ai.agents` per riflettere i tuoi nomi reali

**Esempio con schema personalizzato:**
```sql
-- Agente per schema custom "warehouse"
INSERT INTO chat_ai.agents (name, description, system_prompt, schema_name, tool_names, is_active)
VALUES 
  ('warehouse', 
   'Warehouse inventory management',
   'You are an AI assistant specialized in warehouse management. You have access to the "warehouse" schema...',
   'warehouse',
   'sql_select', 
   1);
```

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

```powershell
python test_setup.py
```

Se vedi `🎉 All tests passed!` il setup è corretto.

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

---

## 💡 Utilizzo dell'applicazione

### Primo Accesso

1. Apri `http://localhost:8501`
2. **Registrazione**: Crea account (tab "Registrazione")
3. **Login**: Accedi con le credenziali
4. **Seleziona Agente**: Sidebar → Scegli tra gli agenti disponibili
5. **Chat**: Scrivi domande in linguaggio naturale

### Sistema Agenti Dinamico in Azione

#### Conversazioni Filtrate per Agente
- Sidebar mostra **solo conversazioni dell'agente corrente**
- Cambiando agente, la lista si aggiorna automaticamente
- Pulsante "Riesegui questa domanda" per rilanciarla come nuova query

#### FAQ Suggerite Intelligenti
- Sezione "FAQ suggerite" nella sidebar
- Basate sulle ultime domande dell'agente corrente
- Pulsante "Genera/aggiorna FAQ" richiama il modello FAQ (es. Haiku)
- Genera domande **senza placeholder**, pronte all'uso
- Click su "Usa questa FAQ" precompila la chat

#### Pannello Admin Agenti (Solo per `admin`)

**Utente admin può:**
1. Selezionare un agente esistente
2. Modificare in tempo reale:
   - **Descrizione** (mostrata nella UI)
   - **System prompt** (comportamento dell'agente)
   - **Modello** (override `AGENT_MODEL` globale)
   - **Tool names** (es. `sql_select,get_schema`)
3. Attivare/disattivare agente
4. Salvare → **Reinizializzazione automatica** senza restart

**Esempi di Modifiche Admin:**

**Cambio prompt per analisi più tecniche:**
```
Original: "Rispondi in modo semplice per utenti business..."
Nuovo: "Fornisci analisi dettagliate con formule statistiche e grafici testuali..."
```

**Override modello per agente specifico:**
```
AGENT_MODEL globale: claude-sonnet-4-5-20250929
Override vendite: claude-opus-4-20250514  # Modello più potente per analytics complesse
```

**Aggiunta tool personalizzato:**
```
tool_names: sql_select
Nuovo: sql_select,get_schema,export_csv
```

### Esempi di Query

**Magazzino:**
```
Mostrami i prodotti con giacenza sotto 10 unità
```

**Ordini:**
```
Quali ordini sono stati creati oggi?
```

**Vendite:**
```
Qual è il fatturato totale di questo mese?
Confrontalo con lo stesso periodo dell'anno scorso
```

---

## 🔌 API principali

### Autenticazione (`/api/auth`)

- `POST /api/auth/register` – Registrazione utente
- `POST /api/auth/login` – Login, restituisce `session_id`

Header richiesto per API protette:
```http
X-Session-ID: <session_id>
```

### Chat (`/api/chat`)

- `GET /api/chat/agents` – Lista agenti disponibili (nome + descrizione)
- `POST /api/chat/stream` – Endpoint SSE streaming:
  - Body: `{ "agent_name", "message", "conversation_id"? }`
  - Salva messaggi e aggiorna `conversation_id`
- `GET /api/chat/conversations?agent_name=vendite` – Lista conversazioni (opzionale filtro)
- `GET /api/chat/conversations/{id}/messages` – Messaggi di una conversazione
- `GET /api/chat/faq_suggestions?agent_name=vendite&limit=50` – FAQ suggerite

### Admin (`/api/admin`)

- `GET /api/admin/agents` – Lista completa configurazioni agenti
- `PUT /api/admin/agents/{agent_id}` – Aggiorna configurazione agente
  - Body: `{ "description", "system_prompt", "model", "tool_names", "is_active" }`
  - Trigger: Reinizializzazione automatica `AgentManager`

---

## 🧪 Test e debugging

### Test di Setup
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python test_setup.py
```

Verifica:
- ✅ Configurazione caricata
- ✅ Connessione database
- ✅ AgentManager inizializzato

### Test Retry Logic (Anthropic 529 Errors)
```powershell
python test_retry_logic.py
```

Simula errori 529 Overloaded e verifica backoff esponenziale.

### Inspect Agent (Debugging Datapizza)
```powershell
python inspect_agent.py
```

Mostra metodi disponibili di `Agent`, `AnthropicClient`, `StepResult`.

---

## 🐛 Troubleshooting

Vedi `QUICKSTART.md` e `TROUBLESHOOTING.md` per guide dettagliate.

### Problemi Comuni

#### Backend non si avvia
- Verifica virtualenv attivo: `.\
```

#### Agente non risponde o dà errori SQL
- Verifica schema SQL configurato (`chat_ai.agents.schema_name`)
- Controlla system_prompt menzioni tabelle/viste corrette
- Usa Admin Panel per testare modifiche al prompt
```
#### Frontend non comunica con backend
- Backend deve essere su `http://localhost:8000`
- Verifica CORS in `backend/app/main.py`
- Test: `curl http://localhost:8000/health`

---

## 📝 Roadmap / Miglioramenti futuri

### Agenti Dinamici
- [x] Configurazione database-driven
- [x] Admin Panel per modifiche runtime
- [x] Reinizializzazione automatica
- [ ] Tool `get_schema` per auto-discovery tabelle
- [ ] Versioning prompt (storico modifiche)
- [ ] A/B testing UI (confronto agenti)

### Sistema
- [ ] Docker/Docker Compose production-ready
- [ ] Test unitari e di integrazione
- [ ] Logging strutturato (structlog)
- [ ] Metriche e monitoring (Prometheus + Grafana)
- [ ] Cache query frequenti (Redis)
- [ ] Rate limiting per utente
- [ ] Export conversazioni
- [ ] Multi-tenancy (workspace isolati)

### AI
- [ ] Streaming token-level vero (non solo risposta finale)
- [ ] Memory conversazionale (oltre messaggi singoli)
- [ ] Function calling avanzato
- [ ] Multi-agent orchestration

---

## 📄 Licenza

Progetto interno – Tutti i diritti riservati.

---

## 👥 Supporto

Per problemi o domande:
- Consulta `QUICKSTART.md`, `STATUS.md`, `TROUBLESHOOTING.md`
- Contatta il team di sviluppo interno

---

## 🎓 Approfondimenti Tecnici

### Datapizza-AI Framework

Il progetto usa [Datapizza-AI](https://docs.datapizza.ai/), un framework Python per:
- Orchestrazione agenti multi-tool
- Supporto multi-provider LLM (OpenAI, Anthropic, Google, Mistral)
- Memory management e context
- Observability con OpenTelemetry

**Documentazione**: https://docs.datapizza.ai/0.0.9/

### Retry Logic Anthropic

`RetryAnthropicClient` wrapper gestisce errori 529 Overloaded:
- Backoff esponenziale: 1s, 2s, 4s, 8s, 16s
- Max 5 tentativi
- Solo per status code 529
- Usa libreria `tenacity`

### Admin Panel Workflow

```
1. Admin modifica prompt in UI
   ↓
2. Frontend POST /api/admin/agents/{id}
   ↓
3. Backend aggiorna chat_ai.agents
   ↓
4. Backend chiama init_agent_manager(settings)
   ↓
5. AgentManager rilegge DB
   ↓
6. Nuove istanze Agent create
   ↓
7. Risposta 200 OK al frontend
   ↓
8. Utenti vedono nuovo comportamento
   (nessun restart richiesto)
```

---

**Versione README:** 2.0 (Sistema Agenti Dinamico)  
**Ultimo aggiornamento:** Novembre 2025