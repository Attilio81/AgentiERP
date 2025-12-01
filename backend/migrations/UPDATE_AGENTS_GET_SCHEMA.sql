-- ========================================
-- SCRIPT: Aggiorna agenti con tool get_schema
-- ========================================
--
-- Questo script aggiunge il tool "get_schema" a tutti gli agenti esistenti
-- che hanno il tool "sql_select" configurato.
--
-- Il tool get_schema permette agli agenti di:
-- - Esplorare autonomamente lo schema del database
-- - Vedere quali tabelle esistono
-- - Ispezionare colonne, tipi di dati, nullable di ogni tabella
-- - Scrivere query SQL più accurate senza dover hardcodare lo schema nel prompt
--
-- PREREQUISITI:
-- - Tabella chat_ai.agents già esistente
-- - Agenti già configurati con tool_names = 'sql_select'
--
-- COME USARE:
-- 1. Backup della tabella agents (opzionale ma consigliato):
--    SELECT * INTO chat_ai.agents_backup FROM chat_ai.agents;
--
-- 2. Esegui questo script:
--    sqlcmd -S your_server -d your_database -i UPDATE_AGENTS_GET_SCHEMA.sql
--
-- 3. Riavvia il backend per ricaricare gli agenti:
--    uvicorn app.main:app --reload
--
-- ========================================

USE [YourDatabase];  -- MODIFICA: inserisci il nome del tuo database
GO

-- Controlla configurazione attuale
PRINT 'Configurazione agenti PRIMA dell''aggiornamento:';
SELECT
    id,
    name,
    tool_names,
    is_active,
    updated_at
FROM chat_ai.agents
ORDER BY name;
GO

-- ========================================
-- AGGIORNAMENTO 1: Aggiungi get_schema a tutti gli agenti con sql_select
-- ========================================
PRINT '';
PRINT 'Aggiornamento 1: Aggiunta tool get_schema agli agenti con sql_select...';

UPDATE chat_ai.agents
SET
    tool_names = 'sql_select,get_schema',  -- Aggiungi get_schema alla lista
    updated_at = GETDATE()
WHERE
    tool_names = 'sql_select'  -- Solo agenti che hanno sql_select
    AND is_active = 1;         -- Solo agenti attivi

PRINT '  ✓ Agenti aggiornati: ' + CAST(@@ROWCOUNT AS VARCHAR(10));
GO

-- ========================================
-- AGGIORNAMENTO 2: (Opzionale) Migliora system_prompt per sfruttare get_schema
-- ========================================
PRINT '';
PRINT 'Aggiornamento 2: Miglioramento system_prompt per utilizzo get_schema...';

-- Questo aggiornamento aggiunge un suggerimento nel prompt per usare get_schema
-- quando l'agente non è sicuro dello schema
UPDATE chat_ai.agents
SET system_prompt = system_prompt +
'

IMPORTANTE - USO DEL TOOL get_schema:
- Se non sei sicuro di quali tabelle o colonne esistano, USA SEMPRE get_schema() prima di scrivere la query SQL.
- get_schema() senza parametri mostra tutte le tabelle disponibili.
- get_schema("NomeTabella") mostra la struttura completa di una tabella specifica.
- Questo ti permette di scrivere query SQL accurate senza indovinare i nomi delle colonne.',
    updated_at = GETDATE()
WHERE
    tool_names LIKE '%get_schema%'  -- Solo agenti che ora hanno get_schema
    AND is_active = 1
    AND system_prompt NOT LIKE '%USO DEL TOOL get_schema%';  -- Evita duplicati se riesegui lo script

PRINT '  ✓ Prompt aggiornati: ' + CAST(@@ROWCOUNT AS VARCHAR(10));
GO

-- ========================================
-- VERIFICA FINALE
-- ========================================
PRINT '';
PRINT 'Configurazione agenti DOPO l''aggiornamento:';
SELECT
    id,
    name,
    tool_names,
    is_active,
    updated_at
FROM chat_ai.agents
ORDER BY name;
GO

PRINT '';
PRINT '========================================';
PRINT '✓ SCRIPT COMPLETATO CON SUCCESSO!';
PRINT '========================================';
PRINT '';
PRINT 'PROSSIMI PASSI:';
PRINT '1. Verifica che tool_names contenga "sql_select,get_schema"';
PRINT '2. Riavvia il backend FastAPI per ricaricare gli agenti';
PRINT '3. Testa un agente chiedendo: "Quali tabelle hai a disposizione?"';
PRINT '   L''agente dovrebbe usare get_schema() per rispondere';
PRINT '';
GO
