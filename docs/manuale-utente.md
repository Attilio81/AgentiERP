# Manuale Utente – AgentiERP

Questo manuale descrive le funzionalità principali dell'interfaccia Streamlit per gli utenti finali (business user e amministratori) del sistema AgentiERP.

## 1. Requisiti e accesso

- Browser moderno (Chrome/Edge/Firefox aggiornato).
- URL Frontend: `http://localhost:8501` (in produzione sostituire con l'indirizzo fornito dall'IT).
- Credenziali personali (username/password) create tramite registrazione o fornite dall'amministratore.

### 1.1 Registrazione
1. Apri la pagina principale e seleziona la tab **"Registrazione"**.
2. Inserisci:
   - Username (min. 3 caratteri, senza spazi).
   - Password (min. 6 caratteri) e conferma password.
3. Premi **"Registrati"**. Se i dati sono corretti, verrai autenticato automaticamente.

### 1.2 Login
1. Seleziona la tab **"Login"**.
2. Inserisci username e password.
3. Premi **"Accedi"**. In caso di credenziali errate, verrà mostrato un messaggio di avviso.

> 🔐 **Sicurezza:** Non condividere le credenziali. Dopo l'utilizzo, effettua sempre il logout dalla sidebar.

## 2. Navigazione dell'interfaccia

La UI è divisa in due aree principali:

1. **Sidebar sinistra** – contiene:
   - Informazioni utente e pulsante **Logout**.
   - Sezione **Seleziona Agente**.
   - Pulsante **"Nuova conversazione"**.
   - Storico **"Conversazioni recenti"** per l'agente scelto.
   - Sezione **"FAQ suggerite"**.
   - (Solo per admin) collegamento al **Pannello Admin**.

2. **Area principale** – mostra la chat con l'agente selezionato:
   - Cronologia messaggi.
   - Input testuale **"Scrivi un messaggio…"** (oppure FAQ selezionata).
   - Risposte generate dall'agente in tempo reale.

## 3. Utilizzo della chat

1. **Seleziona l'agente** adatto alla tua analisi (es. vendite, magazzino, ordini).
2. Premi **"Nuova conversazione"** per iniziare da zero oppure scegli una conversazione recente dalla lista.
3. Scrivi la domanda nel campo chat (es. "Mostrami il fatturato del Q1 2024 suddiviso per canale") e invia.
4. L'agente esegue le query sul database e restituisce la risposta:
   - L'output può includere testo strutturato, tabelle formattate e commenti sui risultati.
   - La conversazione viene salvata automaticamente.

### 3.1 Suggerimenti per domande efficaci
- Specifica periodo, filtri o aggregazioni ("negli ultimi 6 mesi", "per cliente").
- Richiedi confronti temporali o KPI chiari ("confronta con lo stesso mese dello scorso anno").
- Evita linguaggio ambiguo o generico.

### 3.2 Riutilizzo conversazioni
- Usa la sezione **"Conversazioni recenti"** per rivedere fino a 10 richieste precedenti legate all'agente selezionato.
- Il pulsante **"Riesegui questa domanda"** ricarica il testo nella chat come nuova richiesta.

## 4. FAQ suggerite

La sezione **FAQ suggerite** genera automaticamente domande frequenti basate sull'attività recente:
1. Seleziona un agente.
2. Premi **"Genera/aggiorna FAQ"** per creare l'elenco.
3. Espandi ciascuna FAQ per leggerne l'eventuale risposta o premi **"Usa questa FAQ"** per inviarla direttamente in chat.

> ℹ️ Le FAQ vengono calcolate con un modello più leggero per offrire suggerimenti veloci e contestuali.

## 5. Pannello Admin (solo utenti con username `admin`)

1. Dalla sidebar della chat premi **"Apri pannello Admin"**.
2. Seleziona un agente dalla lista.
3. La pagina mostra due colonne:
   - **Dettagli correnti**: informazioni lette dal database (`ID`, descrizione, prompt, stato, tools).
   - **Modifica agente**: form per aggiornare descrizione, system prompt, modello, tools e flag di attivazione.
4. Premi **"Salva modifiche"** per applicare i cambiamenti. L'AgentManager viene reinizializzato automaticamente.
5. Da questa pagina è possibile anche tornare alla chat o effettuare il logout.

> ⚠️ Modifiche errate al prompt o ai tools possono impedire il funzionamento dell'agente. Documenta sempre gli aggiornamenti.

## 6. Risoluzione problemi rapida

| Problema | Possibile causa | Soluzione suggerita |
| --- | --- | --- |
| Non riesco a loggarmi | Credenziali errate o sessione scaduta | Verifica username/password, ripeti il login, se necessario contatta l'amministratore per un reset |
| Nessun agente disponibile | Backend offline o nessun agente attivo | Verifica con l'IT che il backend sia in esecuzione, chiedi a un admin di attivare gli agenti |
| La chat restituisce errori SQL | Domanda ambigua o prompt non aggiornato | Riformula la richiesta con filtri precisi; se l'errore persiste, segnala al team admin |
| FAQ non disponibili | Nessuna domanda recente o errore di rete | Premi "Genera/aggiorna FAQ"; se continua, controlla la connessione Internet |

## 7. Buone pratiche
- Effettua il logout dopo ogni sessione condivisa.
- Prima di modificare agenti o prompt, annota le variazioni (versioning manuale).
- Se un'informazione è critica, valida i risultati confrontandoli con report ufficiali.
- Segnala al team tecnico eventuali risposte incoerenti: potranno aggiornare prompt o rules.

## 8. Supporto
- Manuali tecnici aggiuntivi: `README.md`, `QUICKSTART.md`, `TROUBLESHOOTING.md`.
- Email del team IT o canale interno di supporto.
- In caso di anomalia critica, fornire screenshot, agente utilizzato, testo della domanda e orario.

---
Ultimo aggiornamento manuale: **Novembre 2025**.
