# 🚀 Quick Start Guide

Guida rapida per far partire il sistema in 5 minuti.

## Prerequisiti Veloci

✅ Python 3.10+  
✅ SQL Server accessibile  
✅ ODBC Driver 18 installato  
✅ Chiave API Anthropic  

## Setup in 5 Passi

### 1️⃣ Configura Environment

```bash
# Copia e modifica .env
copy .env.example .env
notepad .env
```

**Modifica questi valori**:
```env
DATABASE_URL=mssql+pyodbc://your_user:your_password@your_server:1433/your_database?driver=ODBC+Driver+18+for+SQL+Server
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
SECRET_KEY=run_this_command_to_generate_key
```

**Genera SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2️⃣ Installa Dipendenze Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3️⃣ Installa Dipendenze Frontend

```bash
cd ..\frontend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
```

### 4️⃣ Inizializza Database

**Opzione A - Con sqlcmd**:
```bash
sqlcmd -S your_server -d your_database -U your_user -P your_password -i backend\app\database\init_schema.sql
```

**Opzione B - Con SSMS**:
1. Apri `backend\app\database\init_schema.sql` in SQL Server Management Studio
2. Modifica la riga 7: `USE [YourDatabaseName];` con il tuo database
3. Esegui lo script (F5)

### 5️⃣ Testa Setup

```bash
python test_setup.py
```

Se vedi "🎉 All tests passed!", sei pronto!

## Avvia l'Applicazione

### Terminal 1 - Backend
```bash
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Aspetta il messaggio: `Uvicorn running on http://127.0.0.1:8000`

### Terminal 2 - Frontend
```bash
cd frontend
.\venv\Scripts\Activate.ps1
streamlit run app.py
```

Il browser si aprirà automaticamente su `http://localhost:8501`

## Primo Utilizzo

1. **Registrati**: Crea un account username/password
2. **Login**: Accedi con le credenziali
3. **Seleziona Agente**: Sidebar → Scegli Magazzino/Ordini/Vendite
4. **Chatta**: Scrivi una domanda in linguaggio naturale!

### Esempi di Query

**Magazzino**:
```
Mostrami i prodotti con giacenza sotto 10 unità
```

**Ordini**:
```
Quali ordini sono stati creati oggi?
```

**Vendite**:
```
Qual è il fatturato totale di questo mese?
```

## Troubleshooting

### ❌ "ModuleNotFoundError"
```bash
# Assicurati di aver attivato il virtual environment
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### ❌ "Database connection failed"
- Verifica DATABASE_URL in `.env`
- Testa connessione: `sqlcmd -S server -U user -P password`
- Controlla che ODBC Driver 18 sia installato

### ❌ "Agent manager initialization failed"
- Verifica ANTHROPIC_API_KEY in `.env`
- Controlla che la chiave sia valida su https://console.anthropic.com

### ❌ Frontend non si connette al backend
- Verifica che backend sia in esecuzione su porta 8000
- Apri http://localhost:8000/health per verificare

## Note Importanti

⚠️ **Schema Database**: Il sistema si aspetta che esistano gli schemi `magazzino`, `ordini`, `vendite` nel tuo SQL Server. Se hai nomi diversi, modifica i file:
- `backend/app/agents/prompts.py`
- `backend/app/agents/sql_tools.py`

⚠️ **Prima esecuzione**: Alla prima query, l'agente potrebbe impiegare qualche secondo in più per inizializzarsi.

⚠️ **Limiti**: Le query sono limitate a 100 risultati e 30 secondi di timeout (configurabile in `config.py`).

## Comandi Utili

```bash
# Verifica health backend
curl http://localhost:8000/health

# Vedi documentazione API
open http://localhost:8000/docs

# Stop backend
Ctrl+C

# Stop frontend
Ctrl+C

# Cleanup sessioni scadute (opzionale)
# Esegui in SQL Server:
# EXEC chat_ai.sp_cleanup_expired_sessions
```

## Supporto

Per la documentazione completa vedi `README.md`

Problemi? Controlla:
1. Tutti i servizi sono in esecuzione?
2. Il file `.env` è configurato correttamente?
3. Il database è accessibile?
4. Gli schemi SQL esistono?

---

**Buon utilizzo! 🎉**
