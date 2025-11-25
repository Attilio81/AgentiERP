# Manuale Utente – AgentiERP
**Versione 2.2 – Novembre 2025**

Questo manuale descrive le funzionalità principali dell'interfaccia Streamlit per gli utenti finali (business user e amministratori) del sistema AgentiERP.

## Novità Versione 2.2 – Fase 2

### 🌐 Ricerca Web (DuckDuckGo)
Gli agenti possono ora cercare informazioni su internet quando i dati non sono disponibili nel database aziendale. Questo permette di:
- Cercare informazioni su prodotti/aziende esterne
- Confrontare prezzi e trend di mercato
- Ottenere dati normativi o legislativi aggiornati
- Integrare dati pubblici con analisi interne

**Tool disponibile:** `web_search` / `duckduckgo`

### 📅 Report Schedulati Automatici
Gli amministratori possono ora configurare l'invio automatico di report via email secondo schedulazioni predefinite:
- Esecuzione automatica di query agli agenti
- Invio email con report HTML formattati
- Schedulazioni flessibili (giornaliere, settimanali, mensili, custom)
- Pannello UI dedicato nel tab Schedulazioni

**Benefici:**
- Report automatici senza intervento manuale
- Aggiornamenti regolari per stakeholder
- Supporto "primo lunedì del mese" e altre schedulazioni avanzate

## Novità Versione 2.1 – Fase 1

### 🧠 Memoria Conversazionale
Gli agenti ora ricordano la cronologia della conversazione e possono rispondere a domande di follow-up senza dover ripetere il contesto. Questo permette analisi più naturali e approfondite.

**Esempio pratico:**
```
Tu: "Mostrami le vendite del 2025"
Agente: [mostra tabella vendite 2025]
Tu: "E nel 2024?"
Agente: [confronta automaticamente con 2024 senza dover ripetere tutto il contesto]
Tu: "Qual è la variazione percentuale?"
Agente: [calcola la variazione basandosi sui dati già discussi]
```

### 🔍 Scoperta Autonoma dello Schema
Gli agenti possono ora esplorare autonomamente la struttura del database usando il tool `get_schema`. Questo significa che possono:
- Scoprire quali tabelle esistono
- Vedere colonne, tipi di dati e vincoli
- Scrivere query SQL più accurate senza dover "indovinare" i nomi delle colonne

### 📊 Debugging Avanzato (Solo Admin)
Gli amministratori possono abilitare il tracing I/O per vedere tutti gli input/output delle chiamate LLM con metriche di latenza. Utile per debugging e ottimizzazione.

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

### 3.1 Memoria Conversazionale – Come Sfruttarla

**Novità 2.1**: Gli agenti ora ricordano l'intera cronologia della conversazione. Questo significa che puoi:

1. **Fare domande di follow-up** senza ripetere il contesto:
   ```
   Prima domanda: "Mostrami le giacenze dell'articolo ABC123"
   [agente risponde con tabella]

   Follow-up: "E nel magazzino secondario?"
   [agente capisce automaticamente che ti riferisci ad ABC123]

   Follow-up: "Confronta con il mese scorso"
   [agente confronta ABC123 tra questo mese e il precedente]
   ```

2. **Esplorare i dati in modo iterativo**:
   ```
   Tu: "Quali sono i 10 articoli più venduti?"
   [agente mostra top 10]

   Tu: "Mostrami il trend mensile del primo articolo"
   [agente prende il codice articolo dal messaggio precedente]

   Tu: "Chi sono i clienti principali per questo articolo?"
   [agente continua l'analisi sullo stesso articolo]
   ```

3. **Raffinare progressivamente le analisi**:
   ```
   Tu: "Analizza le vendite 2025"
   [agente mostra dati completi]

   Tu: "Concentrati solo sul Q1"
   Tu: "Escludi il cliente X"
   Tu: "Raggruppa per settimana invece che per mese"
   [ogni richiesta raffina la precedente senza dover ripetere tutto]
   ```

> 💡 **Suggerimento**: Quando inizi una **nuova analisi su un argomento diverso**, premi "Nuova conversazione" per evitare confusione. Usa la stessa conversazione per approfondire lo stesso argomento.

### 3.2 Suggerimenti per domande efficaci
- Specifica periodo, filtri o aggregazioni ("negli ultimi 6 mesi", "per cliente").
- Richiedi confronti temporali o KPI chiari ("confronta con lo stesso mese dello scorso anno").
- **Sfrutta la memoria**: se hai già menzionato un articolo/cliente/periodo, puoi riferirti ad esso con "quello", "lo stesso", "anche per..."
- Evita linguaggio ambiguo solo nella **prima domanda**; nelle successive l'agente capisce il contesto.

### 3.3 Riutilizzo conversazioni
- Usa la sezione **"Conversazioni recenti"** per rivedere fino a 10 richieste precedenti legate all'agente selezionato.
- Il pulsante **"Riesegui questa domanda"** ricarica il testo nella chat come nuova richiesta.
- **Attenzione**: rieseguire una domanda in una conversazione diversa potrebbe dare risultati differenti se manca il contesto originale.

## 4. FAQ suggerite

La sezione **FAQ suggerite** genera automaticamente domande frequenti basate sull'attività recente:
1. Seleziona un agente.
2. Premi **"Genera/aggiorna FAQ"** per creare l'elenco.
3. Espandi ciascuna FAQ per leggerne l'eventuale risposta o premi **"Usa questa FAQ"** per inviarla direttamente in chat.

> ℹ️ Le FAQ vengono calcolate con un modello più leggero per offrire suggerimenti veloci e contestuali.

## 5. Esempi pratici con l'agente "Magazzino"

L'agente **Magazzino** è configurato con un prompt specializzato sulla gestione operativa delle giacenze. Lavora principalmente sulle viste:

- `magazzino.giacenze`
  - Colonne chiave: `CodiceAzienda`, `CodiceArticolo`, `CodiceMagazzino`, `NumeroLotto`, `Ubicazione`, `EsistenzaLotto`.
- `magazzino.articoli`
  - Colonne chiave: `CodiceArticolo`, `DescrizioneArticolo`, `UnitaMisuraBase`, `CodiceFamiglia`, `DescrizioneFamiglia`, `CodiceFornitore`, `RagioneSocialeFornitore`, `Ubicazione`.

### 5.1 Che cosa fa l'agente Magazzino

Quando fai una domanda all'agente Magazzino, lui:

1. **Analizza il testo della richiesta**.
2. **[NOVITÀ 2.1] Esplora lo schema del database** usando il tool `get_schema` per:
   - Verificare quali tabelle/viste sono disponibili
   - Controllare quali colonne esistono e i loro tipi di dati
   - Scrivere query SQL più accurate senza "indovinare" i nomi
3. **Costruisce una query SQL** in sola lettura usando il tool `sql_select`.
4. Usa sempre gli schemi completi (`magazzino.giacenze`, `magazzino.articoli`).
5. Somma le giacenze con `SUM(EsistenzaLotto)` raggruppando per `CodiceArticolo`.
6. Esclude i lotti con `EsistenzaLotto = 0` (esauriti), salvo tu lo chieda esplicitamente.
7. **Restituisce una risposta** sempre nel formato:
   1. Tabella markdown (Codice, Descrizione, Giacenza, Ubicazione, UM...).
   2. Spiegazione testuale (totali, medie, situazioni critiche).
   3. Eventuali alert (es. giacenze negative, articolo non trovato).

> 🔍 **Vantaggio get_schema**: Se chiedi informazioni su una colonna che non conosci (es. "C'è un campo data scadenza?"), l'agente può esplorare lo schema autonomamente invece di rispondere "Non so". Questo rende le analisi più complete e accurate.

### 5.2 Esempi di domande utili

Di seguito alcuni esempi che puoi letteralmente copiare/incollare nella chat quando sei sull'agente **Magazzino**.

#### Esempio 1 – Giacenza di un singolo articolo

> **Domanda:**
> "Mostrami la giacenza disponibile per l'articolo `ABC123` nel magazzino principale."

Cosa farà l'agente:

- Userà `magazzino.giacenze` filtrando per `CodiceArticolo = 'ABC123'` e magazzino principale.
- Calcolerà `Giacenza disponibile = SUM(EsistenzaLotto) WHERE EsistenzaLotto > 0`.
- Aggregherà i lotti e aggiungerà le descrizioni da `magazzino.articoli`.
- Ordinerà per giacenza decrescente.

Esempio di output atteso:

| Codice | Descrizione                | Giacenza | Ubicazioni              | UM |
| ------ | -------------------------- | -------- | ----------------------- | -- |
| ABC123 | Articolo di esempio 123   | 150      | MAG-01 / MAG-02 / MAG-3 | PZ |

Interpretazione (testo sotto la tabella):

> "Per l'articolo **ABC123** hai **150 pezzi disponibili** distribuiti su **3 ubicazioni** (MAG-01, MAG-02, MAG-3). Non risultano giacenze negative né lotti esauriti." 

Se la somma risultasse 0, l'agente dovrebbe scrivere chiaramente qualcosa come:

> "L'articolo **ABC123** risulta **ESAURITO** (giacenza totale = 0)."

#### Esempio 2 – Articoli sotto scorta o critici

> **Domanda:**
> "Elenca gli articoli con giacenza molto bassa (meno di 10 pezzi) evidenziando quelli con giacenza zero come ESAURITI."

Cosa farà l'agente:

- Calcolerà la giacenza totale per articolo con `SUM(EsistenzaLotto)`.
- Considererà come **ESAURITI** gli articoli con giacenza = 0.
- Metterà in evidenza situazioni critiche (es. meno di 10 pezzi).

Esempio di tabella:

| Codice | Descrizione              | Giacenza | Stato       | Ubicazione principale |
| ------ | ------------------------ | -------- | ----------- | ---------------------- |
| XYZ001 | Articolo stagionale X    | 0        | ESAURITO    | MAG-01                 |
| LMN050 | Ricambio critico LMN050  | 7        | BASSA SCORTA| MAG-02                 |

Sotto la tabella l'agente dovrebbe spiegare:

> "Hai **1 articolo esaurito** (XYZ001) e **1 articolo in bassa scorta** (LMN050 con 7 pezzi). Valuta un riordino urgente per LMN050."

#### Esempio 3 – Giacenze per famiglia o fornitore

> **Domanda:**
> "Mostrami la giacenza aggregata per famiglia articolo, ordinata dalla più disponibile alla meno disponibile."

Oppure:

> **Domanda:**
> "Per il fornitore `FORN001`, quali articoli ho a magazzino e con quanta giacenza?"

L'agente sfrutterà le colonne di `magazzino.articoli` (`CodiceFamiglia`, `DescrizioneFamiglia`, `CodiceFornitore`, `RagioneSocialeFornitore`) per raggruppare e descrivere i dati.

Esempio di output sintetico (per famiglia):

| CodiceFamiglia | DescrizioneFamiglia    | GiacenzaTotale |
| -------------- | ---------------------- | -------------- |
| FAM001         | Ricambi critici        | 320            |
| FAM002         | Prodotti finiti        | 180            |

Interpretazione:

> "La famiglia **Ricambi critici (FAM001)** è quella con maggiore disponibilità (320 pezzi totali), seguita dai **Prodotti finiti (FAM002)** con 180 pezzi."

#### Esempio 4 – Ricerca per codice parziale

> **Domanda:**
> "Cerca tutti gli articoli che contengono 'FILTRO' nella descrizione e mostrami la giacenza disponibile."

Se il codice o la descrizione fornita non esiste esattamente, l'agente può proporre alternative usando condizioni tipo `LIKE '%FILTRO%'`.

Esempio di alert atteso:

> "Non trovo l'articolo esatto richiesto, ma ho trovato questi articoli simili che contengono 'FILTRO' nella descrizione."

#### Esempio 5 – Conversazione multi-step con memoria (NOVITÀ 2.1)

Questo esempio mostra come sfruttare la **memoria conversazionale** per approfondire un'analisi senza ripetere il contesto.

**Conversazione completa:**

> **Tu (messaggio 1):**
> "Mostrami la giacenza disponibile per l'articolo ABC123"

**Risposta agente:**

| Codice | Descrizione              | Giacenza | Ubicazioni       | UM |
| ------ | ------------------------ | -------- | ---------------- | -- |
| ABC123 | Articolo di esempio 123  | 150      | MAG-01, MAG-02   | PZ |

> L'articolo **ABC123** ha **150 pezzi disponibili** distribuiti su 2 ubicazioni.

---

> **Tu (messaggio 2 – follow-up):**
> "E nel magazzino secondario?"

**Risposta agente:**

> Nel **magazzino secondario (MAG-02)** l'articolo **ABC123** ha **45 pezzi disponibili**.

> 💡 **Nota**: Non hai dovuto ripetere "ABC123"! L'agente ricorda che stai parlando di quell'articolo.

---

> **Tu (messaggio 3 – altro follow-up):**
> "Mostrami lo storico movimenti dell'ultimo mese"

**Risposta agente:**

> Ecco i movimenti di **ABC123** nell'ultimo mese:
> - 2025-10-15: Carico 200 pz (da fornitore F001)
> - 2025-10-22: Scarico -50 pz (ordine cliente C123)
> - 2025-11-03: Scarico -55 pz (ordine cliente C456)

---

> **Tu (messaggio 4 – raffinamento):**
> "Confronta con lo stesso periodo dell'anno scorso"

**Risposta agente:**

> **Confronto ABC123 – Ottobre-Novembre 2024 vs 2025:**
> - 2024: Giacenza media 180 pz, rotazione 2.1x
> - 2025: Giacenza media 150 pz, rotazione 2.5x
>
> L'articolo ha **migliorato la rotazione** del 19% ma la giacenza media è **scesa del 17%**.

---

**Vantaggi di questa modalità:**
- ✅ Non ripeti codice articolo, magazzino, periodo in ogni messaggio
- ✅ Approfondisci l'analisi in modo naturale come una conversazione
- ✅ L'agente capisce il contesto e raffina progressivamente la risposta
- ✅ Risparmi tempo e rendi l'interazione più fluida

> ⚠️ **Quando fare "Nuova conversazione"**: Se vuoi analizzare un **articolo completamente diverso** (es. passare da ABC123 a XYZ789 per un'analisi indipendente), premi "Nuova conversazione" per evitare che l'agente confonda i contesti. 

### 5.3 Come interpretare correttamente le risposte

Quando usi l'agente Magazzino, verifica sempre:

- **Colonne della tabella**: controlla che ci siano almeno Codice, Descrizione, Giacenza, Ubicazione, UM.
- **Totali**: nelle note testuali dovresti trovare un riepilogo numerico (es. "150 pezzi totali", "3 ubicazioni").
- **Alert**: presta attenzione a messaggi tipo "ESAURITO", "giacenza negativa", "ubicazione mancante".

Se una risposta non rispetta questo formato (es. niente tabella, niente interpretazione testuale), segnala al team tecnico: potrebbe essere necessario affinare il prompt dell'agente o controllare la configurazione in Admin.

## 6. Pannello Admin (solo utenti con username `admin`)

1. Dalla sidebar della chat premi **"Apri pannello Admin"**.
2. Seleziona un agente dalla lista.
3. La pagina mostra due colonne:
   - **Dettagli correnti**: informazioni lette dal database (`ID`, descrizione, prompt, stato, tools).
   - **Modifica agente**: form per aggiornare descrizione, system prompt, modello, tools e flag di attivazione.
4. Premi **"Salva modifiche"** per applicare i cambiamenti. L'AgentManager viene reinizializzato automaticamente.
5. Da questa pagina è possibile anche tornare alla chat o effettuare il logout.

> ⚠️ Modifiche errate al prompt o ai tools possono impedire il funzionamento dell'agente. Documenta sempre gli aggiornamenti.

### 6.1 Debugging Avanzato – I/O Tracing (NOVITÀ 2.1)

Gli amministratori possono abilitare il **tracing dettagliato** di tutte le chiamate LLM per debugging e ottimizzazione.

**Come abilitare:**
1. Nel file `.env` del backend, imposta: `ENABLE_LLM_TRACING=True`
2. Riavvia il backend FastAPI
3. Tutti gli input/output delle chiamate LLM verranno loggati nei log del backend con:
   - Timestamp preciso (millisecondi)
   - Latenza della chiamata (ms)
   - Input inviato all'LLM (troncato se troppo lungo)
   - Output ricevuto dall'LLM (troncato se troppo lungo)

**Quando usarlo:**
- ✅ Debugging di risposte inaspettate o errori
- ✅ Ottimizzazione delle performance (analisi latenza)
- ✅ Verifica che il prompt system e i tool siano configurati correttamente
- ✅ Analisi dei costi (conta token, durata chiamate)

**Attenzioni:**
- ⚠️ **Genera log molto grandi**: non abilitare in produzione per periodi prolungati
- ⚠️ **Può contenere dati sensibili**: i log includeranno query SQL e risultati
- ⚠️ **Solo per debugging**: disabilitare dopo aver risolto il problema

**Esempio di log I/O:**
```
================================================================================
[2025-11-23 14:32:16.847] [I/O TRACE] RESPONSE
[LATENCY] 1724.53ms
[CONTENT] Per l'articolo ABC123 ho trovato una giacenza di 150 pezzi...
```

### 6.2 Schedulazioni Report (NOVITÀ 2.2)

Gli amministratori possono configurare report automatici che vengono eseguiti secondo schedulazioni predefinite e inviati via email.

**Come accedere:**
1. Login come utente `admin`
2. Apri pannello Admin
3. Seleziona tab **"📅 Schedulazioni"**

**Operazioni disponibili:**

#### Creazione nuova schedulazione

1. Click su **"➕ Nuova Schedulazione"**
2. Compila il form:
   - **Nome**: Identificativo descrittivo (es. "Report Vendite Mensile")
   - **Descrizione**: Opzionale, dettagli aggiuntivi
   - **Agente**: Seleziona l'agente da utilizzare
   - **Domanda/Query**: La domanda che verrà posta all'agente
   - **Frequenza**: Scegli tra preset o cron expression custom
   - **Email destinatari**: Indirizzi separati da virgola
   - **Schedulazione attiva**: Checkbox per abilitare/disabilitare

3. Click su **"💾 Salva"**

**Preset frequenza disponibili:**
- Ogni giorno alle 09:00
- Ogni lunedì alle 09:00
- **Primo lunedì del mese alle 09:00** (utile per report mensili)
- Primo giorno del mese alle 09:00
- Custom (cron expression manuale)

**Esempio configurazione:**
```
Nome: Report Top 10 Prodotti
Agente: vendite
Prompt: Mi dici i top 10 articoli venduti dal inizio mese?
Frequenza: Primo lunedì del mese alle 09:00
Email: direzione@azienda.com, commerciale@azienda.com
```

#### Test schedulazione

Prima di attivare una schedulazione, puoi testarla:
1. Trova la schedulazione nell'elenco
2. Click su **"🧪 Test"**
3. Il sistema esegue immediatamente la query e invia l'email
4. Verifica che il report sia corretto prima di attivarlo

#### Monitoraggio esecuzioni

Ogni schedulazione mostra:
- **Ultima esecuzione**: Data e ora
- **Status**: success / failed / pending
- **Prossima esecuzione**: Calcolata automaticamente
- **Errore**: Dettagli se l'esecuzione è fallita

**Best practices:**
- ✅ Usa descrizioni chiare per identificare rapidamente le schedulazioni
- ✅ Testa sempre con button "Test" prima di attivare
- ✅ Verifica che gli indirizzi email siano corretti
- ✅ Per report mensili, usa "primo lunedì del mese" invece di "giorno 1" (evita weekend)
- ⚠️ Non schedulare troppe query contemporaneamente (max 5-10 in parallelo)
- ⚠️ Monitora regolarmente lo status delle esecuzioni per individuare errori

**Formato email inviata:**
I report vengono inviati come email HTML professionali con:
- Header con nome schedulazione
- Informazioni agente e data esecuzione
- Domanda eseguita
- Risposta completa dell'agente con tabelle formattate
- Footer informativo



## 7. Risoluzione problemi rapida

| Problema | Possibile causa | Soluzione suggerita |
| --- | --- | --- |
| Non riesco a loggarmi | Credenziali errate o sessione scaduta | Verifica username/password, ripeti il login, se necessario contatta l'amministratore per un reset |
| Nessun agente disponibile | Backend offline o nessun agente attivo | Verifica con l'IT che il backend sia in esecuzione, chiedi a un admin di attivare gli agenti |
| La chat restituisce errori SQL | Domanda ambigua o prompt non aggiornato | Riformula la richiesta con filtri precisi; se l'errore persiste, segnala al team admin |
| FAQ non disponibili | Nessuna domanda recente o errore di rete | Premi "Genera/aggiorna FAQ"; se continua, controlla la connessione Internet |
| **L'agente non ricorda conversazioni precedenti** | Memoria conversazionale non funzionante | Verifica che la conversazione sia la stessa (non hai premuto "Nuova conversazione"). Se il problema persiste, verifica con l'admin che il backend sia aggiornato alla versione 2.1 |
| **L'agente dice "Non so quali colonne esistono"** | Tool get_schema non configurato | L'admin deve aggiungere `get_schema` ai tool dell'agente (vedi `UPDATE_AGENTS_GET_SCHEMA.sql`). Se l'agente ha get_schema ma non lo usa, potrebbe essere un problema di prompt |
| **Risposte molto lente (> 10 secondi)** | Database lento o query complesse | Prova a semplificare la domanda o filtrare per periodi più brevi. Se hai abilitato `ENABLE_LLM_TRACING=True`, disabilitalo (solo per debugging) |
| **L'agente "confonde" contesti di conversazioni diverse** | Stai usando la stessa conversazione per argomenti diversi | Premi "Nuova conversazione" quando cambi completamente argomento (es. da analisi magazzino ad analisi vendite) |

## 8. Buone pratiche

### Generali
- Effettua il logout dopo ogni sessione condivisa.
- Prima di modificare agenti o prompt, annota le variazioni (versioning manuale).
- Se un'informazione è critica, valida i risultati confrontandoli con report ufficiali.
- Segnala al team tecnico eventuali risposte incoerenti: potranno aggiornare prompt o rules.

### Utilizzo della Memoria Conversazionale (NOVITÀ 2.1)
- ✅ **Usa la stessa conversazione** per approfondire lo stesso argomento con domande di follow-up
- ✅ **Premi "Nuova conversazione"** quando cambi completamente argomento (es. da magazzino a vendite)
- ✅ **Sfrutta i pronomi** ("quello", "lo stesso", "anche per...") nelle domande successive - l'agente ricorda il contesto
- ❌ **Non mescolare argomenti diversi** nella stessa conversazione (causa confusione)
- ❌ **Non aspettarti memoria tra conversazioni diverse** - ogni conversazione è isolata

### Ottimizzazione delle Query
- ✅ **Fidati del tool get_schema**: se l'agente ha questo tool, può scoprire autonomamente le colonne disponibili
- ✅ **Chiedi esplorazioni progressive**: "Quali tabelle hai?", poi "Mostrami la struttura di magazzino.giacenze"
- ✅ **Richiedi confronti temporali** sfruttando la memoria: prima chiedi dati 2025, poi "E nel 2024?", poi "Qual è la variazione?"
- ❌ **Non hardcodare troppi dettagli** se l'agente può scoprirli da solo (es. invece di "usa la colonna EsistenzaLotto", chiedi "Mostrami le giacenze" e lascia che l'agente esplori lo schema)

## 9. Supporto
- **Manuali tecnici per utenti business**:
  - `README.md` – Panoramica generale del progetto
  - `docs/manuale-utente.md` – Questo manuale (versione 2.1)
- **Documentazione tecnica per sviluppatori/admin**:
  - `QUICKSTART.md` – Setup rapido
  - `TROUBLESHOOTING.md` – Risoluzione problemi tecnici
  - `FASE1_IMPROVEMENTS.md` – Dettagli tecnici sulle novità Fase 1 (memoria, get_schema, tracing)
- **Supporto interno**:
  - Email del team IT o canale interno di supporto
  - In caso di anomalia critica, fornire screenshot, agente utilizzato, testo della domanda e orario

---

## Changelog

### Versione 2.2 (Novembre 2025) – Fase 2
- 🌐 **Ricerca Web (DuckDuckGo)**: Tool `web_search` per cercare informazioni esterne
- 📅 **Report Schedulati**: Configurazione invio automatico report via email
- 📧 **Email Service**: Template HTML professionali per report
- ⏰ **Supporto Cron Avanzato**: "Primo lunedì del mese" e altre schedulazioni custom
- 🎯 **Test Schedulazioni**: Pulsante test per esecuzione immediata prima dell'attivazione

### Versione 2.1 (Novembre 2025) – Fase 1
- 🧠 **Memoria conversazionale**: Gli agenti ricordano la cronologia e supportano domande di follow-up
- 🔍 **Schema discovery** (tool `get_schema`): Esplorazione autonoma della struttura database
- 📊 **I/O Tracing**: Logging dettagliato chiamate LLM per debugging (solo admin)

### Miglioramenti
- Esempi pratici di conversazioni multi-step nella sezione Magazzino
- Nuove best practice per sfruttare memoria e schema discovery
- Troubleshooting ampliato con scenari Fase 1
- Documentazione admin per configurazione I/O tracing

---
**Ultimo aggiornamento**: Novembre 2025 – Versione 2.1
