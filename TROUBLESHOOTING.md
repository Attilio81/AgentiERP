# Problemi Comuni e Soluzioni

## ⚠️ Errore Python 3.13: `__static_attributes__`

**Sintomo**: 
```
AssertionError: ... but has additional attributes {'__static_attributes__', '__firstlineno__'}
```

**Causa**: Python 3.13 è troppo recente e ha incompatibilità con alcune dipendenze (SQLAlchemy, Pydantic).

**Soluzioni**:

### Opzione 1: Installa Python 3.11 (Consigliata)

1. Scarica Python 3.11.x da https://www.python.org/downloads/
2. Durante l'installazione, seleziona "Add Python 3.11 to PATH"
3. Ricrea i virtual environment:

```powershell
# Backend
cd backend
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install fastapi uvicorn[standard] datapizza-ai anthropic sqlalchemy pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart

# Frontend
cd ..\frontend
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install streamlit requests
```

### Opzione 2: Aggiorna alle ultime versioni compatibili

```powershell
cd backend
pip install --upgrade sqlalchemy pydantic pydantic-settings pydantic-core
```

### Opzione 3: Usa pyenv per gestire versioni Python multiple

```powershell
# Installa pyenv-win
pip install pyenv-win --target %USERPROFILE%\.pyenv
pyenv install 3.11.9
pyenv local 3.11.9
```

## Altri Problemi Comuni

### pyodbc compilation error

**Soluzione**: pyodbc è già installato (5.3.0) nella versione di sistema. Questa versione funziona correttamente.

### Streamlit/numpy compilation error

**Soluzione**: Streamlit e requests sono già installati e funzionano.

## Verifica Versione Python

```powershell
python --version
# Dovrebbe mostrare: Python 3.11.x
```
