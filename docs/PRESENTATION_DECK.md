# AgentiERP – Presentation Deck
**AI-Powered Business Intelligence for SQL Server**

Questo documento contiene i contenuti per creare una presentazione commerciale di AgentiERP. Ogni sezione rappresenta una o più slide.

---

## SLIDE 1: Cover / Titolo

**Titolo principale:**
# AgentiERP
**Conversational AI for Business Intelligence**

**Sottotitolo:**
Trasforma il tuo database SQL Server in un assistente intelligente.
Nessun codice SQL, solo domande in linguaggio naturale.

**Visual suggerito:**
- Screenshot dell'interfaccia chat con una domanda tipo "Mostrami le giacenze sotto scorta"
- Logo AgentiERP
- Immagine stilizzata di grafico + chat bubble

---

## SLIDE 2: Il Problema

### 📊 Il Paradosso dei Dati Aziendali

**Tutti i dati sono nel database, ma...**

❌ **Dipendenza tecnica**
→ Ogni domanda richiede uno sviluppatore o un analista SQL

❌ **Tempo di risposta lento**
→ Giorni o settimane per report ad-hoc

❌ **Dashboard statiche**
→ BI tradizionale mostra solo KPI predefiniti

❌ **Barriera linguistica**
→ SQL non è per tutti, ma i dati servono a tutti

**Il risultato?**
> Le decisioni aziendali si basano su dati vecchi o incompleti.

---

## SLIDE 3: La Soluzione – AgentiERP

### 💬 Parla con i tuoi dati in Italiano

**AgentiERP trasforma SQL Server in un assistente intelligente:**

✅ **Domande in linguaggio naturale**
"Mostrami le giacenze sotto scorta" → Query SQL automatica

✅ **Risposte immediate**
Analisi in secondi, non in giorni

✅ **Zero dipendenze tecniche**
Business user autonomi, IT libera tempo

✅ **Memoria conversazionale** (NOVITÀ v2.1)
Follow-up naturali: "E nel 2024?" "Confronta con il trimestre scorso"

✅ **Scoperta autonoma dello schema**
L'agente esplora il database e scrive query accurate

---

## SLIDE 4: Come Funziona

### 🎯 Architettura Semplice, Risultati Potenti

```
┌─────────────────────────────────────────────────────────────┐
│  1. BUSINESS USER                                           │
│  Scrive domanda in chat: "Fatturato Q1 per cliente?"      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  2. AGENTE AI (Specializzato per dominio)                  │
│  • Analizza la richiesta                                   │
│  • Esplora schema DB (get_schema)                          │
│  • Genera query SQL ottimizzata                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  3. SQL SERVER                                              │
│  Esegue query (SOLO lettura, sicurezza garantita)         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  4. RISPOSTA STRUTTURATA                                    │
│  • Tabella formattata                                       │
│  • Interpretazione testuale                                 │
│  • Alert su anomalie (es. giacenze negative)               │
└─────────────────────────────────────────────────────────────┘
```

**Tecnologie:**
- **Backend:** FastAPI + Datapizza-AI (multi-provider LLM)
- **Frontend:** Streamlit (interfaccia intuitiva)
- **Database:** SQL Server (100% compatibile)
- **AI:** Claude, GPT-4, modelli custom (configurabile)

---

## SLIDE 5: Caso d'Uso Real-World – Magazzino

### 📦 Da Questa Richiesta...

**Business User (responsabile magazzino):**
> "Mostrami la giacenza disponibile per l'articolo ABC123"

**Agente Magazzino:**

| Codice | Descrizione              | Giacenza | Ubicazioni       | UM |
|--------|--------------------------|----------|------------------|----|
| ABC123 | Articolo di esempio 123  | 150      | MAG-01, MAG-02   | PZ |

> L'articolo **ABC123** ha **150 pezzi disponibili** distribuiti su 2 ubicazioni.

---

### 🧠 ...A Conversazione Multi-Step (v2.1)

**Follow-up 1:** "E nel magazzino secondario?"
→ Agente: *45 pezzi in MAG-02*

**Follow-up 2:** "Mostrami lo storico movimenti dell'ultimo mese"
→ Agente: *+200 carico, -105 scarichi*

**Follow-up 3:** "Confronta con lo stesso periodo dell'anno scorso"
→ Agente: *Giacenza media -17%, rotazione +19%*

**Tempo totale:** < 2 minuti
**Valore:** Decisione immediata su riordino scorte

---

## SLIDE 6: Funzionalità Distintive v2.1

### 🚀 Cosa Ci Distingue dalla Concorrenza

| Funzionalità | AgentiERP v2.2 | Competitor Tipici |
|-------------|----------------|-------------------|
| **Memoria conversazionale** | ✅ Follow-up senza ripetere contesto |  ⚠️ Limitata o assente |
| **Schema discovery** | ✅ Esplorazione autonoma DB | ❌ Schema hardcodato in prompt |
| **Web search integrato** | ✅ DuckDuckGo per dati esterni | ⚠️ Raro, spesso a pagamento |
| **Report schedulati** | ✅ Email automatiche con cron avanzato | ⚠️ Solo in piani enterprise |
| **Multi-agente** | ✅ Agenti specializzati per dominio | ⚠️ Singolo chatbot generico |
| **Database-driven config** | ✅ Modifica agenti senza riavvio | ❌ Richiede deployment |
| **Self-hosted** | ✅ Dati rimangono in azienda | ❌ Cloud obbligatorio (GDPR risk) |
| **Admin Panel integrato** | ✅ Modifica prompt/tool da UI | ❌ Solo via codice |
| **Multi-provider LLM** | ✅ Claude, GPT-4, custom | ⚠️ Locked-in su un provider |
| **I/O Tracing** |  ✅ Debug dettagliato (v2.1) | ❌ Black-box |
| **Costo** | 💰 Solo API LLM pay-per-use | 💰💰 Subscription per utente |

---

## SLIDE 7: Analisi Competitiva

### 🔍 Prodotti Simili sul Mercato (2025)

#### **Cloud SaaS (Costo Alto)**

**BlazeSQL** – $499/mese Team Advanced
- ✅ UI professionale
- ❌ Cloud-only, vendor lock-in
- ❌ Costo elevato per PMI

**AskYourDatabase** – Focus CEO/CTO
- ✅ Onboarding rapido
- ❌ Dati in cloud
- ❌ Meno customizzabile

**Text2SQL.ai** – $4-$17/mese
- ✅ Economico per singoli utenti
- ❌ Non enterprise-ready
- ❌ Nessun multi-agente

#### **Enterprise Platform**

**Snowflake Cortex Analyst**
- ✅ Integrato in Snowflake
- ❌ Richiede migrazione a Snowflake
- ❌ Costo infrastrutturale elevato

**Microsoft SQL Server 2025 Copilot**
- ✅ Integrato in SSMS
- ❌ Solo per developer, non business user
- ❌ Nessuna conversational memory

**Google Cloud Conversational Analytics API**
- ✅ Potente NL2SQL
- ❌ Richiede BigQuery/Looker
- ❌ Vendor lock-in Google

#### **Open Source**

**WrenAI (Canner)** – GitHub open-source
- ✅ Gratis, GenBI completo
- ❌ Self-hosting complesso
- ❌ Supporto community-only

**MindsDB** – Open-source
- ✅ Flessibile, multi-database
- ❌ Curva apprendimento ripida
- ❌ Richiede competenze ML

---

### 🎯 Posizionamento AgentiERP

**"Enterprise Features, SMB Accessibility"**

✅ **Self-hosted** → Dati sicuri, GDPR-compliant
✅ **Database-driven** → Flessibilità enterprise
✅ **UI business-friendly** → Adoption rapida
✅ **Costo contenuto** → Solo API LLM usage
✅ **SQL Server native** → Zero migrazione

**Target ideale:**
- PMI italiane con SQL Server esistente
- Aziende manifatturiere (magazzino, produzione)
- Distributori (vendite, logistica)
- Finance teams (controllo di gestione)

---

## SLIDE 8: ROI e Benefici Misurabili

### 💰 Ritorno sull'Investimento

#### **Risparmio Tempo IT**
- **Prima:** 5-10 report ad-hoc/settimana × 2h ciascuno = **10-20h/settimana**
- **Dopo:** Business user autonomi → **~90% richieste risolte self-service**
- **Risparmio:** €500-1000/settimana di tempo IT (riallocabile su progetti strategici)

#### **Velocità Decisionale**
- **Prima:** 2-5 giorni per report → decisioni ritardate
- **Dopo:** < 2 minuti per analisi → decisioni real-time
- **Impatto:** Riduzione stock-out, ottimizzazione riordini, identificazione trend

#### **Democratizzazione Dati**
- **Prima:** 5-10 persone con accesso analisi (tecnici)
- **Dopo:** 50+ persone possono interrogare dati (business user)
- **Valore:** Data-driven culture aziendale

#### **Costi**
- **Setup:** 1-2 giorni installazione + configurazione agenti
- **Running:** Solo costo API LLM (~€0.10-0.50 per conversazione)
- **Zero licensing fee** per utenti aggiuntivi

**Break-even:** 2-4 settimane in azienda media (50+ dipendenti)

---

## SLIDE 9: Sicurezza e Compliance

### 🔒 Enterprise-Grade Security

✅ **Solo Query in Lettura**
→ Nessun rischio di modifiche accidentali al database

✅ **Self-Hosted On-Premise**
→ Dati non lasciano mai l'infrastruttura aziendale

✅ **Multi-Tenant Isolation**
→ Schema-level filtering: ogni agente vede solo "le sue" tabelle

✅ **Autenticazione Integrata**
→ Username/password hashed (bcrypt), sessioni sicure

✅ **Audit Trail Completo**
→ Ogni query SQL loggata con timestamp, utente, agente

✅ **GDPR Compliant**
→ Nessun data export verso cloud esterni

✅ **I/O Tracing Opzionale**
→ Debug dettagliato su richiesta (disabilitabile in produzione)

**Certificazioni future:**
- ISO 27001 (Information Security)
- SOC 2 Type II (se richiesto da clienti enterprise)

---

## SLIDE 10: Roadmap Prodotto

### 🗺️ Evolvere Insieme ai Clienti

#### **✅ FASE 1 – COMPLETATA (v2.1)**
- ✅ Memoria conversazionale
- ✅ Schema discovery (get_schema)
- ✅ I/O tracing per debugging
- ✅ Admin panel per configurazione agenti

#### **✅ FASE 2 – COMPLETATA (v2.2 - Novembre 2025)**
- ✅ **🌐 Web Search integrato** (DuckDuckGo) - Confronto prezzi competitor, trend mercato
- ✅ **📧 Report schedulati** - Email giornaliere/settimanali/mensili automatiche
- ✅ **⏰ Cron avanzato** - "Primo lunedì del mese" e schedulazioni custom
- ✅ **📊 Template email HTML** - Report professionali formattati

#### **🚧 FASE 3 – IN SVILUPPO (Q1 2026)**
- 📊 **Grafici dinamici** (Chart.js/Plotly integration)
- 📄 **Export report** (Excel, PDF)
- 🔍 **RAG su documentazione** (manuali tecnici, specifiche prodotto)

#### **📋 FASE 4 – PIANIFICATA (Q2 2026)**
- 🤖 **Agenti proattivi** (alert automatici su KPI critici)
- 🔗 **Integrazioni** (Slack, Teams, Telegram bot)
- 🎨 **Dashboard builder** (trasforma conversazioni in dashboard persistenti)

#### **🔮 FASE 4 – VISIONE (Q3-Q4 2025)**
- 🧪 **Scenario planning** ("Simula aumento prezzo 10%")
- 📈 **Forecasting ML** (previsioni vendite, scorte)
- 🔄 **Write-back selettivo** (approvazione workflow per UPDATE)
- 🌍 **Multi-database** (oltre SQL Server: PostgreSQL, MySQL)

---

## SLIDE 11: Case Study (Template)

### 📊 Caso Studio: [Nome Azienda Cliente]

**Industria:** Manifatturiero / Distribuzione
**Dimensioni:** 150 dipendenti, 5M€ fatturato
**Database:** SQL Server 2019, 200GB dati operativi

#### **Challenge**
- Responsabili magazzino dipendevano da IT per analisi giacenze
- Report manuali Excel con dati vecchi di 1-2 giorni
- 15-20 richieste ad-hoc/settimana al team IT

#### **Soluzione**
- Deploy AgentiERP v2.1 (2 giorni setup)
- Configurati 3 agenti: Magazzino, Vendite, Acquisti
- Training 1 ora per 10 key users

#### **Risultati (3 mesi)**
- ✅ **90% riduzione** richieste IT per report
- ✅ **< 2 minuti** tempo medio per analisi (vs 2-3 giorni)
- ✅ **€12K risparmiati** in tempo IT (Q1 2025)
- ✅ **15% riduzione** stock-out (decisioni più rapide su riordini)

**Testimonianza:**
> "Prima aspettavamo giorni per sapere cosa riordinare. Ora il responsabile magazzino interroga AgentiERP la mattina e decide in autonomia. Un game-changer." – [CTO / IT Manager]

---

## SLIDE 12: Pricing (Proposta Commerciale)

### 💳 Modello di Pricing Trasparente

#### **Setup Iniziale**
**€2.500 - €5.000** (one-time)
- Installazione backend + frontend
- Configurazione SQL Server connection
- Setup 3-5 agenti iniziali
- Training 2h per admin + 1h per key users
- Documentazione personalizzata

#### **Running Costs**
**Solo costo API LLM** (pay-per-use)
- ~€0.10-0.50 per conversazione (dipende da modello)
- Esempio: 500 conversazioni/mese = €50-250/mese
- **Nessun costo per utente aggiuntivo**
- **Nessuna subscription fee**

#### **Supporto & Manutenzione (Opzionale)**
**€300-500/mese**
- Aggiornamenti di versione
- Configurazione nuovi agenti
- Supporto prioritario (8h response time)
- Review trimestrale performance

#### **Confronto Competitor**

| Soluzione | Setup | Costo Mensile (20 utenti) |
|-----------|-------|---------------------------|
| **AgentiERP** | €3.5K | €100-300 (API only) |
| BlazeSQL | €0 (SaaS) | €499 + €50/utente = €1.500 |
| AskYourDatabase | €0 (SaaS) | €800-1.200 |
| Custom development | €15-30K | €500-1.000 (manutenzione) |

**ROI:** Break-even 2-3 mesi per azienda media

---

## SLIDE 13: Getting Started

### 🚀 Inizia in 3 Passi

#### **1. DISCOVERY CALL (30 min)**
- Analisi use case principali
- Verifica requisiti tecnici (SQL Server version, schema DB)
- Demo live su dati di esempio

#### **2. PILOT (2 settimane)**
- Setup ambiente test
- Configurazione 1-2 agenti pilota
- Testing con 3-5 key users
- Valutazione risultati

#### **3. PRODUCTION ROLLOUT (1 settimana)**
- Deploy ambiente produzione
- Configurazione agenti finali
- Training team allargato
- Go-live e supporto

**Timeline totale:** 3-4 settimane da kick-off a full adoption

---

## SLIDE 14: Tech Stack (Per CTO/IT Manager)

### ⚙️ Dettagli Tecnici

#### **Backend**
- **Framework:** FastAPI (Python 3.11+)
- **AI Orchestration:** Datapizza-AI (multi-provider)
- **Database Driver:** pyodbc + SQLAlchemy
- **Auth:** Custom user management (bcrypt)
- **API:** RESTful + Server-Sent Events (SSE streaming)

#### **Frontend**
- **Framework:** Streamlit 1.30+
- **UI:** Responsive web app
- **State Management:** Session-based

#### **AI/LLM**
- **Primary:** Anthropic Claude Sonnet 4.5
- **Alternative:** OpenAI GPT-4, custom models
- **Tools:** Function calling (SQL execution, schema discovery)

#### **Database**
- **Supported:** SQL Server 2016+ (compatibilità testata)
- **Access:** Read-only queries (sicurezza)
- **Schema:** INFORMATION_SCHEMA per discovery

#### **Infrastructure Requirements**
- **Server:** Linux/Windows con Docker (opzionale)
- **RAM:** 4GB minimo, 8GB raccomandato
- **Network:** Accesso SQL Server + Internet (API LLM)
- **Ports:** 8000 (backend), 8501 (frontend)

#### **Deployment**
- Docker Compose (recommended)
- Systemd services (Linux)
- Manual Python venv

---

## SLIDE 15: FAQ

### ❓ Domande Frequenti

**Q: AgentiERP può modificare i dati nel database?**
A: No. Tutti gli agenti eseguono **solo query SELECT** (read-only). Nessun rischio di modifiche accidentali.

**Q: I nostri dati vengono inviati a servizi cloud esterni?**
A: Solo le **domande e i risultati** (non i dati raw) vengono inviati all'API LLM per l'analisi. Il database rimane on-premise. Per massima privacy, è possibile usare modelli LLM self-hosted.

**Q: Funziona con database diversi da SQL Server?**
A: Al momento supportiamo **SQL Server**. PostgreSQL e MySQL sono nella roadmap Fase 4 (Q4 2025).

**Q: Quanti agenti posso configurare?**
A: Illimitati. Ogni agente può essere specializzato per dominio (vendite, magazzino, HR, finance...).

**Q: Cosa succede se l'agente genera una query SQL errata?**
A: L'agente riceve l'errore SQL e **riprova automaticamente** con una query corretta. La memoria conversazionale v2.1 aiuta a raffinare iterativamente.

**Q: Posso personalizzare i prompt degli agenti?**
A: Sì, tramite **Admin Panel** (web UI) o direttamente nel database. Nessun coding richiesto.

**Q: Quale latenza devo aspettarmi?**
A: **2-5 secondi** per domande semplici, **5-15 secondi** per analisi complesse (dipende da query DB + latenza API LLM).

**Q: È compatibile con Active Directory / LDAP?**
A: Non ancora. Auth nativa username/password. AD/LDAP è nella roadmap Fase 3.

---

## SLIDE 16: Social Proof (Template)

### 🌟 Cosa Dicono i Clienti

> "AgentiERP ha trasformato il nostro modo di gestire il magazzino. Prima dovevamo aspettare giorni per avere report, ora i responsabili decidono in autonomia in pochi minuti."
> **— [Nome], CFO @ [Azienda Manifatturiera]**

---

> "Abbiamo ridotto del 90% le richieste di report ad-hoc al team IT. Il ROI è stato raggiunto in meno di 2 mesi."
> **— [Nome], CTO @ [Distributore]**

---

> "L'interfaccia è così intuitiva che anche i nostri responsabili meno tech-savvy la usano quotidianamente. Zero training necessario."
> **— [Nome], Operations Manager @ [PMI 150 dipendenti]**

---

### 📊 Metriche di Successo

- **12** clienti attivi (Novembre 2025)
- **4.8/5** soddisfazione media
- **87%** riduzione media tempo-a-insight
- **€450K** valore analizzato cumulativo (risparmi IT clienti)

*(Nota: Personalizzare con metriche reali quando disponibili)*

---

## SLIDE 17: Competitive Advantages Summary

### 🏆 Perché Scegliere AgentiERP

| Vantaggio | Descrizione | Impatto Business |
|-----------|-------------|------------------|
| **🧠 Memoria Conversazionale** | Follow-up senza ripetere contesto | UX naturale, analisi più rapide |
| **🔍 Schema Discovery** | Esplorazione autonoma DB | Query accurate senza hardcoding |
| **🏢 Self-Hosted** | Dati rimangono in azienda | GDPR compliance, zero vendor lock-in |
| **⚡ Database-Driven** | Config agenti senza deployment | Time-to-market ridotto 90% |
| **🛠️ Admin Panel** | Modifica prompt da UI | Autonomia business, zero coding |
| **💰 Pay-Per-Use** | Solo costo API LLM | TCO 60-80% inferiore vs SaaS |
| **🔒 Read-Only Queries** | Sicurezza by-design | Zero rischio data corruption |
| **🌐 Multi-Provider LLM** | Claude, GPT-4, custom | Flessibilità, no vendor lock-in |

---

## SLIDE 18: Call to Action

### 📞 Parliamone!

**Vuoi vedere AgentiERP in azione sui tuoi dati?**

#### **Prossimi Passi:**

1. **📅 Prenota Demo Gratuita (30 min)**
   Vediamo insieme come AgentiERP può trasformare il tuo business

2. **🧪 Pilot Gratuito (2 settimane)**
   Testiamo su 1-2 use case reali con i tuoi key users

3. **🚀 Go-Live in 3 Settimane**
   Dalla discovery al rollout produzione

---

### **Contatti**

📧 **Email:** [info@agentierp.it]
🌐 **Website:** [www.agentierp.it]
💼 **LinkedIn:** [linkedin.com/company/agentierp]
📱 **Tel:** [+39 XXX XXXXXXX]

---

**Trasforma i tuoi dati in conversazioni.**
**AgentiERP – AI-Powered Business Intelligence**

---

## APPENDICE: Fonti Ricerca Competitiva

### Prodotti Analizzati (Novembre 2025)

**Cloud SaaS:**
- [BlazeSQL AI](https://www.blazesql.com/)
- [AskYourDatabase](https://www.askyourdatabase.com/)
- [Text2SQL.ai](https://www.text2sql.ai/)
- [SQLAI.ai](https://www.sqlai.ai/)

**Enterprise Platforms:**
- [Snowflake Cortex Analyst](https://www.snowflake.com/en/product/use-cases/ai-powered-bi/)
- [Google Cloud Conversational Analytics API](https://cloud.google.com/blog/products/business-intelligence/use-conversational-analytics-api-for-natural-language-ai)
- [SQL Server 2025 Copilot](https://www.trustedtechteam.com/blogs/sql-server/sql-server-2025-ai-developer-tools-copilot-langchain)

**Open Source:**
- [WrenAI (Canner)](https://github.com/Canner/WrenAI)
- [MindsDB](https://mindsdb.com/)

**Articoli di Settore:**
- [Best 6 Tools for Conversational AI Analytics](https://www.blazesql.com/blog/best-conversational-ai-analytics-tools)
- [Top AI-powered database query tools 2025](https://tsttechnology.io/blog/insights-with-ai-chatbot)
- [Comparison of Top 4 SQL AI Tools](https://medium.com/@sheldonniu/comparison-of-the-top-4-sql-ai-tools-in-2024-ba7fb75dd6e0)
- [Best SQL AI Tools 2025 Complete Guide](https://www.text2sql.ai/best-text-to-sql-tools-2025)

---

## NOTE PER LA GRAFICA

### Palette Colori Suggerita
- **Primary:** Blu scuro professionale (#1E3A8A)
- **Accent:** Verde tecnologico (#10B981)
- **Background:** Bianco/Grigio chiaro (#F9FAFB)
- **Text:** Grigio scuro (#1F2937)

### Font Suggeriti
- **Heading:** Inter Bold / Montserrat Bold
- **Body:** Inter Regular / Open Sans
- **Code/Tech:** Fira Code / JetBrains Mono

### Visual Elements
- Screenshot interfaccia chat reali
- Diagrammi architettura con icone moderne
- Grafici ROI con colori contrastanti
- Icone flat design (es. Heroicons, Font Awesome)
- Foto stock professionali team business (evitare stock photos troppo generiche)

### Formato Slide
- **PowerPoint:** 16:9 widescreen
- **PDF:** Export per condivisione via email
- **Keynote:** Mac-friendly per demo live

---

**Documento creato:** Novembre 2025
**Versione:** 1.0 (basato su AgentiERP v2.1)
**Autore:** AgentiERP Team
