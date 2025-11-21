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

## 5. Esempi pratici con l'agente "Magazzino"

L'agente **Magazzino** è configurato con un prompt specializzato sulla gestione operativa delle giacenze. Lavora principalmente sulle viste:

- `magazzino.giacenze`
  - Colonne chiave: `CodiceAzienda`, `CodiceArticolo`, `CodiceMagazzino`, `NumeroLotto`, `Ubicazione`, `EsistenzaLotto`.
- `magazzino.articoli`
  - Colonne chiave: `CodiceArticolo`, `DescrizioneArticolo`, `UnitaMisuraBase`, `CodiceFamiglia`, `DescrizioneFamiglia`, `CodiceFornitore`, `RagioneSocialeFornitore`, `Ubicazione`.

### 5.1 Che cosa fa l'agente Magazzino

Quando fai una domanda all'agente Magazzino, lui:

1. Analizza il testo della richiesta.
2. Costruisce una query SQL **solo in lettura** usando il tool `sql_select`.
3. Usa sempre gli schemi completi (`magazzino.giacenze`, `magazzino.articoli`).
4. Somma le giacenze con `SUM(EsistenzaLotto)` raggruppando per `CodiceArticolo`.
5. Esclude i lotti con `EsistenzaLotto = 0` (esauriti), salvo tu lo chieda esplicitamente.
6. Restituisce una risposta sempre nel formato:
   1. Tabella markdown (Codice, Descrizione, Giacenza, Ubicazione, UM...).
   2. Spiegazione testuale (totali, medie, situazioni critiche).
   3. Eventuali alert (es. giacenze negative, articolo non trovato).

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

## 7. Risoluzione problemi rapida

| Problema | Possibile causa | Soluzione suggerita |
| --- | --- | --- |
| Non riesco a loggarmi | Credenziali errate o sessione scaduta | Verifica username/password, ripeti il login, se necessario contatta l'amministratore per un reset |
| Nessun agente disponibile | Backend offline o nessun agente attivo | Verifica con l'IT che il backend sia in esecuzione, chiedi a un admin di attivare gli agenti |
| La chat restituisce errori SQL | Domanda ambigua o prompt non aggiornato | Riformula la richiesta con filtri precisi; se l'errore persiste, segnala al team admin |
| FAQ non disponibili | Nessuna domanda recente o errore di rete | Premi "Genera/aggiorna FAQ"; se continua, controlla la connessione Internet |

## 8. Buone pratiche
- Effettua il logout dopo ogni sessione condivisa.
- Prima di modificare agenti o prompt, annota le variazioni (versioning manuale).
- Se un'informazione è critica, valida i risultati confrontandoli con report ufficiali.
- Segnala al team tecnico eventuali risposte incoerenti: potranno aggiornare prompt o rules.

## 9. Supporto
- Manuali tecnici aggiuntivi: `README.md`, `QUICKSTART.md`, `TROUBLESHOOTING.md`.
- Email del team IT o canale interno di supporto.
- In caso di anomalia critica, fornire screenshot, agente utilizzato, testo della domanda e orario.

---
Ultimo aggiornamento manuale: **Novembre 2025**.
