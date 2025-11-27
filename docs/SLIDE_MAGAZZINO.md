# 📦 Chat del Magazzino – AgentiERP
**Presentazione Demo Live**

---

## SLIDE 1: Copertina

# 📦 Chat del Magazzino
**Gestione Giacenze Intelligente con AI**

**AgentiERP v2.2 – Novembre 2025**

> Trasforma la gestione del magazzino in una semplice conversazione.
> Zero codice SQL, solo domande in italiano.

**Credenziali Demo:**
- **Utente:** Admin
- **Password:** pass123456

---

## SLIDE 2: Il Problema

### 🚨 Sfide Quotidiane del Magazzino

**Prima di AgentiERP:**

❌ **Reportistica manuale:**
- Ogni verifica giacenza richiede un tecnico IT
- Export Excel con dati vecchi di ore/giorni
- Impossibile ottenere risposte immediate

❌ **Mancanza di visibilità:**
- Quanti pezzi dell'articolo ABC123?
- Quali articoli sono sotto scorta?
- Dove si trova materiale specifico?

❌ **Decisioni ritardate:**
- Riordini in ritardo → Stock-out
- Eccesso di scorte → Capitale immobilizzato
- Tempo perso in chiamate e email al reparto IT

**Il risultato?**
> Perdite economiche, inefficienze operative, stress inutile.

---

## SLIDE 3: La Soluzione – Chat Magazzino

### 💬 Parla con il tuo Magazzino in Italiano

**L'Agente Magazzino di AgentiERP ti permette di:**

✅ **Domande dirette in linguaggio naturale**
- "Mostrami la giacenza disponibile per ABC123"
- "Quali articoli sono sotto scorta?"
- "Dove si trova il materiale nella famiglia ricambi?"

✅ **Risposte immediate in secondi**
- Tabelle formattate con articoli, giacenze, ubicazioni
- Interpretazione testuale dei dati
- Alert automatici su situazioni critiche

✅ **Zero competenze tecniche richieste**
- Nessun SQL da scrivere
- Nessun export manuale
- Nessuna dipendenza da IT

✅ **Memoria conversazionale** (NOVITÀ v2.1)
- Domande di follow-up senza ripetere contesto
- "E nel magazzino secondario?" → L'agente ricorda l'articolo

---

## SLIDE 4: Come Funziona

### 🎯 Workflow dell'Agente Magazzino

```
┌─────────────────────────────────────────────────────────────┐
│  1. RESPONSABILE MAGAZZINO                                  │
│  Scrive: "Mostrami giacenza disponibile per ABC123"       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  2. AGENTE MAGAZZINO AI                                     │
│  • Analizza la domanda                                      │
│  • Esplora schema DB con get_schema (auto-discovery)       │
│  • Genera query SQL su magazzino.giacenze + articoli       │
│  • Esegue query in READ-ONLY (sicurezza garantita)        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  3. SQL SERVER                                              │
│  Calcola: SUM(EsistenzaLotto) GROUP BY CodiceArticolo     │
│  Filtra: EsistenzaLotto > 0 (solo disponibilità reale)    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  4. RISPOSTA STRUTTURATA                                    │
│  • Tabella: Codice | Descrizione | Giacenza | Ubicazioni  │
│  • Interpretazione: "150 pezzi in 3 ubicazioni"           │
│  • Alert: "ESAURITO" / "Giacenza negativa" se necessario  │
└─────────────────────────────────────────────────────────────┘
```

**Tempo totale:** < 5 secondi dalla domanda alla risposta

---

## SLIDE 5: Funzionalità Chiave

### 🔍 Cosa Può Fare l'Agente Magazzino

#### 1️⃣ **Verifica Giacenze**
**Domanda:** "Mostrami la giacenza disponibile per l'articolo ABC123"

**Risposta:**

| Codice | Descrizione              | Giacenza | Ubicazioni       | UM |
|--------|--------------------------|----------|------------------|-----|
| ABC123 | Articolo di esempio 123  | 150      | MAG-01, MAG-02   | PZ  |

> L'articolo **ABC123** ha **150 pezzi disponibili** distribuiti su **2 ubicazioni**.

---

#### 2️⃣ **Identificazione Criticità**
**Domanda:** "Elenca gli articoli con giacenza molto bassa (meno di 10 pezzi)"

**Risposta:**

| Codice | Descrizione              | Giacenza | Stato        | Ubicazione |
|--------|--------------------------|----------|--------------|------------|
| XYZ001 | Articolo stagionale X    | 0        | 🔴 ESAURITO  | MAG-01     |
| LMN050 | Ricambio critico LMN050  | 7        | ⚠️ BASSA SCORTA | MAG-02  |

> **1 articolo esaurito** e **1 articolo in bassa scorta**. Valuta riordino urgente.

---

#### 3️⃣ **Analisi per Famiglia/Fornitore**
**Domanda:** "Giacenza aggregata per famiglia articolo"

| CodiceFamiglia | DescrizioneFamiglia | GiacenzaTotale |
|----------------|---------------------|----------------|
| FAM001         | Ricambi critici     | 320            |
| FAM002         | Prodotti finiti     | 180            |

> La famiglia **Ricambi critici** ha la maggiore disponibilità (320 pezzi).

---

#### 4️⃣ **Ricerca Intelligente**
**Domanda:** "Cerca tutti gli articoli che contengono 'FILTRO' nella descrizione"

> Mostra tutti gli articoli con descrizione simile anche se il codice esatto non esiste.

---

## SLIDE 6: Memoria Conversazionale (NOVITÀ v2.1)

### 🧠 Conversazioni Multi-Step Naturali

**Esempio di Follow-up senza Ripetizioni:**

---

**Tu:** "Mostrami la giacenza disponibile per l'articolo ABC123"

**Agente:**
| Codice | Descrizione              | Giacenza | Ubicazioni       | UM |
|--------|--------------------------|----------|------------------|-----|
| ABC123 | Articolo di esempio 123  | 150      | MAG-01, MAG-02   | PZ  |

---

**Tu:** "E nel magazzino secondario?"  
*(Non hai dovuto ripetere "ABC123"!)*

**Agente:**
> Nel **magazzino secondario (MAG-02)** l'articolo **ABC123** ha **45 pezzi disponibili**.

---

**Tu:** "Mostrami lo storico movimenti dell'ultimo mese"

**Agente:**
> Ecco i movimenti di **ABC123** nell'ultimo mese:
> - 2025-10-15: Carico +200 pz (da fornitore F001)
> - 2025-10-22: Scarico -50 pz (ordine C123)
> - 2025-11-03: Scarico -55 pz (ordine C456)

---

**Tu:** "Confronta con lo stesso periodo dell'anno scorso"

**Agente:**
> **Confronto ABC123 – Ottobre-Novembre 2024 vs 2025:**
> - 2024: Giacenza media 180 pz, rotazione 2.1x
> - 2025: Giacenza media 150 pz, rotazione 2.5x
>
> L'articolo ha **migliorato la rotazione** del 19% ma la giacenza media è **scesa del 17%**.

---

**Vantaggio:** ✅ Analisi approfondite senza ripetere contesto ad ogni domanda

---

## SLIDE 7: Schema Discovery Automatica (NOVITÀ v2.1)

### 🔍 L'Agente Esplora il Database da Solo

**Prima (sistema tradizionale):**
- Schema hardcodato nel prompt
- Modifiche al DB richiedono aggiornamenti manuali
- Risposte "Non so se quella colonna esiste"

**Ora (con tool `get_schema`):**

✅ **Auto-discovery delle tabelle:**
```
Domanda: "Quali tabelle hai a disposizione?"
Agente usa: get_schema("")

Risultato automatico:
TABLE_SCHEMA | TABLE_NAME      | TABLE_TYPE
magazzino    | giacenze        | BASE TABLE
magazzino    | articoli        | BASE TABLE
magazzino    | movimenti       | BASE TABLE
```

✅ **Esplorazione struttura:**
```
Domanda: "Mostrami la struttura della tabella giacenze"
Agente usa: get_schema("giacenze")

Risultato:
COLUMN_NAME       | DATA_TYPE | IS_NULLABLE
CodiceArticolo    | varchar   | NO
EsistenzaLotto    | decimal   | NO
Ubicazione        | varchar   | YES
NumeroLotto       | varchar   | YES
```

✅ **Vantaggi:**
- Nessun hardcoding → Flessibilità massima
- Query SQL più accurate → Meno errori
- Funziona con qualsiasi database → Scalabilità

---

## SLIDE 8: Sicurezza e Compliance

### 🔒 Sicurezza By-Design

✅ **Solo Query READ-ONLY (SELECT)**
- Nessun INSERT, UPDATE, DELETE, DROP
- Validazione automatica prima dell'esecuzione
- Zero rischio di modifiche accidentali

✅ **Isolation per Schema**
- Agente Magazzino vede SOLO schema `magazzino.*`
- Agente Vendite vede SOLO schema `vendite.*`
- Nessun accesso cross-schema non autorizzato

✅ **Audit Trail Completo**
- Ogni query loggata con timestamp, utente, agente
- Tracciabilità totale delle operazioni

✅ **Self-Hosted On-Premise**
- Dati rimangono nel tuo SQL Server
- Zero export verso cloud esterni (GDPR compliant)
- Solo domande/risposte inviate all'API LLM

✅ **Autenticazione Integrata**
- Username/password hashate (bcrypt)
- Sessioni sicure con scadenza configurabile

---

## SLIDE 9: ROI e Benefici Misurabili

### 💰 Impatto sul Business

#### **Prima di AgentiERP:**
- ⏱️ **2-3 giorni** per ottenere un report giacenze personalizzato
- 👨‍💻 **5-10 richieste/settimana** al team IT
- 📊 **Decisioni ritardate** su riordini e ottimizzazioni

#### **Dopo AgentiERP:**
- ⚡ **< 5 secondi** per qualsiasi analisi giacenze
- 🎯 **90% riduzione** richieste IT per report magazzino
- 💡 **Decisioni real-time** basate su dati aggiornati

---

### **Esempio Case Study:**

**Azienda Manifatturiera – 150 dipendenti**

**Risultati dopo 3 mesi:**
- ✅ **15% riduzione stock-out** (decisioni più rapide su riordini)
- ✅ **€12K risparmiati** in tempo IT (Q1 2025)
- ✅ **< 2 minuti** tempo medio per analisi giacenze (vs 2-3 giorni)
- ✅ **10+ responsabili** autonomi invece di dipendere da 2 tecnici IT

**ROI:** Break-even in **meno di 2 mesi**

---

## SLIDE 10: Come Iniziare

### 🚀 Accesso alla Chat Magazzino

#### **Step 1: Login**
1. Apri `http://localhost:8501`
2. Inserisci credenziali:
   - **Username:** Admin
   - **Password:** pass123456
3. Click su **"Accedi"**

---

#### **Step 2: Seleziona Agente Magazzino**
1. Sidebar sinistra → **"Seleziona Agente"**
2. Scegli **"magazzino"** dal menu
3. Click su **"Nuova conversazione"**

---

#### **Step 3: Inizia a Chiedere**
Esempi di domande pronte all'uso:

```
✅ Mostrami la giacenza disponibile per l'articolo ABC123
✅ Quali articoli sono sotto scorta?
✅ Elenca gli articoli con giacenza meno di 10 pezzi
✅ Giacenza aggregata per famiglia articolo
✅ Cerca tutti gli articoli che contengono "FILTRO"
✅ Quali sono gli articoli esauriti nel magazzino principale?
```

---

#### **Step 4: Esplora con Follow-up**
Dopo la prima risposta, approfondisci:
```
➡️ E nel magazzino secondario?
➡️ Mostrami lo storico movimenti
➡️ Confronta con il mese scorso
```

---

## SLIDE 11: FAQ Rapide

### ❓ Domande Frequenti

**Q: Posso modificare i dati del magazzino tramite la chat?**
A: No. L'agente esegue **solo query SELECT** (lettura). Nessun rischio di modifiche accidentali.

---

**Q: I dati sono aggiornati in tempo reale?**
A: Sì. Ogni query interroga **direttamente SQL Server** con i dati più recenti.

---

**Q: Cosa succede se chiedo qualcosa che non esiste nel DB?**
A: L'agente ti avvisa: "Articolo non trovato" oppure suggerisce articoli simili.

---

**Q: L'agente ricorda le conversazioni precedenti?**
A: Sì! Nella **stessa conversazione** ricorda tutto il contesto. Per argomenti diversi, premi **"Nuova conversazione"**.

---

**Q: Posso usare la chat anche senza conoscere SQL?**
A: Assolutamente sì! Scrivi in **italiano naturale**, l'agente genera il SQL automaticamente.

---

**Q: Quanto tempo ci vuole per una risposta?**
A: **2-5 secondi** per domande semplici, **5-15 secondi** per analisi complesse.

---

## SLIDE 12: Roadmap Futura

### 🗺️ Prossimi Miglioramenti Chat Magazzino

#### **✅ GIÀ DISPONIBILI (v2.2)**
- ✅ Memoria conversazionale
- ✅ Schema discovery automatica
- ✅ Report schedulati via email
- ✅ Ricerca web DuckDuckGo (dati esterni)

---

#### **🚧 IN SVILUPPO (Q1 2026)**
- 📊 **Grafici dinamici** delle giacenze (trend, rotazioni)
- 📄 **Export Excel/PDF** dei report giacenze
- 🔍 **RAG su manuali tecnici** (es. "Qual è la shelf-life di ABC123?")

---

#### **📋 PIANIFICATO (Q2 2026)**
- 🤖 **Alert proattivi** automatici:
  - "Articolo XYZ sotto scorta minima"
  - "Giacenza negativa rilevata"
  - "Lotto in scadenza tra 7 giorni"
- 📱 **Integrazioni Telegram/Slack** (chat magazzino via bot)
- 📈 **Forecasting ML** (previsione fabbisogno scorte)

---

## SLIDE 13: Demo Live – Esempi Pratici

### 🎬 Prova Subito con Questi Esempi

#### **Esempio 1: Verifica Giacenza Singolo Articolo**
```
Domanda: Mostrami la giacenza disponibile per l'articolo ABC123
```
**Risultato atteso:**
- Tabella con codice, descrizione, giacenza, ubicazioni, UM
- Interpretazione testuale: "150 pezzi in 2 ubicazioni"

---

#### **Esempio 2: Articoli Critici**
```
Domanda: Elenca gli articoli con giacenza meno di 10 pezzi evidenziando quelli esauriti
```
**Risultato atteso:**
- Tabella con stato (ESAURITO / BASSA SCORTA)
- Alert: "1 articolo esaurito, 1 in bassa scorta. Valuta riordino urgente"

---

#### **Esempio 3: Analisi per Famiglia**
```
Domanda: Giacenza aggregata per famiglia articolo, ordinata dalla più disponibile
```
**Risultato atteso:**
- Tabella raggruppata per CodiceFamiglia, DescrizioneFamiglia, GiacenzaTotale
- Interpretazione: "Famiglia Ricambi critici ha maggiore disponibilità (320 pz)"

---

#### **Esempio 4: Conversazione Multi-Step**
```
1. "Mostrami giacenze articolo ABC123"
2. "E nel magazzino secondario?" (follow-up senza ripetere codice)
3. "Mostrami storico movimenti ultimo mese"
4. "Confronta con anno scorso"
```
**Risultato atteso:**
- Analisi progressiva senza ripetere contesto
- Confronto temporale con variazioni percentuali

---

## SLIDE 14: Supporto e Documentazione

### 📚 Risorse Disponibili

#### **Manuali Utente:**
- 📄 **Manuale Utente Completo** (`docs/manuale-utente.md`)
  - Sezione dedicata "Agente Magazzino"
  - Esempi pratici commentati
  - Best practices

#### **Documentazione Tecnica (Solo Admin):**
- 📄 `README.md` – Panoramica sistema
- 📄 `FASE1_IMPROVEMENTS.md` – Novità v2.1 (Memory, get_schema, I/O Tracing)
- 📄 `QUICKSTART.md` – Setup rapido
- 📄 `TROUBLESHOOTING.md` – Risoluzione problemi

#### **Supporto:**
- 📧 **Email:** [info@agentierp.it]
- 💬 **Canale interno:** Team IT
- 🛠️ **Admin Panel:** Configurazione avanzata agente Magazzino

---

## SLIDE 15: Call to Action

### 🎯 Inizia Ora!

#### **Accedi alla Demo:**

1. **Apri browser** → `http://localhost:8501`
2. **Login:**
   - Username: `Admin`
   - Password: `pass123456`
3. **Seleziona agente:** `magazzino`
4. **Scrivi la tua prima domanda!**

---

### **Domande Suggerite per Iniziare:**

```
🟢 Facili:
   → Mostrami la giacenza disponibile per ABC123
   → Quali articoli sono sotto scorta?

🟡 Medie:
   → Giacenza aggregata per famiglia articolo
   → Cerca articoli che contengono "FILTRO"

🔴 Avanzate (con follow-up):
   → Mostrami top 10 articoli per giacenza
   → E solo nel magazzino principale? (follow-up)
   → Confronta con il mese scorso (follow-up)
```

---

### **Trasforma il tuo magazzino in una conversazione.**

**📦 Chat Magazzino – AgentiERP v2.2**

---

## NOTE PRESENTAZIONE

### Suggerimenti per il Presentatore:

1. **Slide 1-3:** Introduzione e problema (3 min)
2. **Slide 4-7:** Funzionalità chiave e novità (5 min)
3. **Slide 8-9:** Sicurezza e ROI (3 min)
4. **Slide 10-13:** Demo live pratica (10 min)
5. **Slide 14-15:** Documentazione e call to action (2 min)

**Tempo totale:** ~25 minuti con Q&A

### Visual Suggeriti:
- Screenshot interfaccia chat reale
- GIF animate delle conversazioni multi-step
- Diagrammi flusso workflow
- Grafici ROI e metriche

### Palette Colori:
- **Primary:** #1E3A8A (Blu professionale)
- **Accent:** #10B981 (Verde tecnologico)
- **Alert:** #DC2626 (Rosso per criticità)
- **Success:** #059669 (Verde scuro per conferme)

---

**Documento creato:** Novembre 2025  
**Versione:** 1.0 (AgentiERP v2.2)  
**Autore:** AgentiERP Team
