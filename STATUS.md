# ✅ Sistema Operativo - Python 3.13

## 🎉 Sistema Completamente Funzionante!

Entrambi i servizi sono ora in esecuzione su Python 3.13:

### Backend FastAPI
- **URL**: http://127.0.0.1:8000
- **Docs**: http://127.0.0.1:8000/docs
- **Health**: http://127.0.0.1:8000/health
- **Agenti**: magazzino, ordini, vendite

### Frontend Streamlit
- **Local URL**: http://localhost:8501
- **Network URL**: http://192.168.44.126:8501

## Compatibilità Python 3.13

Dopo l'aggiornamento delle dipendenze, tutto funziona perfettamente:

| Pacchetto | Versione Aggiornata | Compatibile Python 3.13 |
|-----------|---------------------|-------------------------|
| SQLAlchemy | 2.0.44 | ✅ Sì |
| Pydantic | 2.12.4 | ✅ Sì |
| FastAPI | 0.115.8 | ✅ Sì |
| Uvicorn | 0.38.0 | ✅ Sì |
| Anthropic | 0.74.1 | ✅ Sì |
| Streamlit | Latest | ✅ Sì |

## Come Testare

**1. Apri il browser**: http://localhost:8501

**2. Registrati** nella tab "Registrazione":
- Username: scegli un nome
- Password: minimo 6 caratteri

**3. Seleziona un agente** dalla sidebar:
- Magazzino
- Ordini
- Vendite

**4. Scrivi una domanda**, ad esempio:
```
Mostrami le prime 10 righe della tabella principale
```

**5. Osserva la risposta** che arriva in streaming mentre l'agente:
- Analizza la richiesta
- Costruisce la query SQL
- Esegue la query
- Formatta i risultati
- Risponde in italiano

## File di Configurazione

### File .env
Posizione: `/backend/.env` (copiato dalla root)
```
DATABASE_URL=mssql+pyodbc://user:password@server:1433/database?driver=ODBC+Driver+18+for+SQL+Server
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
SECRET_KEY=your-secret-key-here-minimum-32-characters
```

### Database Schema
- Schema creato: `chat_ai`
- Tabelle: `users`, `sessions`, `conversations`, `messages`
- Stored Procedure: `sp_cleanup_expired_sessions`

## Comandi Rapidi

### Avvia Backend
```powershell
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Avvia Frontend
```powershell
cd frontend
streamlit run app.py
```

### Stop Servizi
Entrambi: `Ctrl+C` nel rispettivo terminale

## Note Tecniche

✅ **Problema risolto**: Incompatibilità iniziali con Python 3.13 risolte aggiornando le dipendenze alle ultime versioni

✅ **pyodbc**: Utilizzata la versione 5.3.0 già installata nel sistema (evitato errore compilazione)

✅ **.env**: Necessario in `backend/.env` per permettere a pydantic-settings di trovarlo quando uvicorn parte da quella directory

✅ **CORS**: Configurato per permettere comunicazione frontend-backend

## Prossimi Passi

1. **Personalizza gli schemi SQL**: Se gli schemi del tuo database non si chiamano `magazzino`, `ordini`, `vendite`, modifica:
   - `backend/app/agents/prompts.py`
   - `backend/app/agents/sql_tools.py`

2. **Testa con query reali**: Interroga il tuo database VITC con domande in linguaggio naturale

3. **Monitora i log**: Osserva il terminale del backend per vedere le query SQL generate

4. **Esplora le conversazioni**: La cronologia viene salvata nel database e caricata automaticamente

Buon utilizzo! 🚀
