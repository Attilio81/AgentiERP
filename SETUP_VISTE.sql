-- ============================================================================
-- SCRIPT DI CONFIGURAZIONE VISTE PER AGENTI AI
-- ============================================================================
-- Questo script crea un livello di astrazione (Viste) sopra le tue tabelle reali.
-- L'AI interrogherà queste viste (es. magazzino.prodotti) invece delle tabelle complesse.
--
-- ISTRUZIONI:
-- 1. Sostituisci [TuaTabellaReale] con i nomi veri delle tue tabelle (es. MG_Articoli)
-- 2. Sostituisci [ColonnaReale] con i nomi veri delle colonne
-- 3. Esegui questo script nel database VITC
-- ============================================================================

USE VITC;
GO

-- 1. Crea gli schemi logici (se non esistono)
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'magazzino') EXEC('CREATE SCHEMA [magazzino]');
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'ordini') EXEC('CREATE SCHEMA [ordini]');
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'vendite') EXEC('CREATE SCHEMA [vendite]');
GO

-- ============================================================================
-- AGENTE MAGAZZINO
-- ============================================================================

-- Vista PRODOTTI (Mappa la tua anagrafica articoli)
CREATE OR ALTER VIEW magazzino.prodotti AS
SELECT 
    -- Mappa qui i tuoi campi reali
    CodiceArticolo      AS codice,          -- es. AR_Codice
    Descrizione         AS descrizione,     -- es. AR_Descrizione
    UnitaMisura         AS um,              -- es. AR_UnitaMisura
    GiacenzaAttuale     AS giacenza,        -- es. MG_Giacenza
    ScortaMinima        AS scorta_minima,   -- es. MG_ScortaMin
    CostoUltimo         AS costo            -- es. AR_CostoUltimo
FROM 
    dbo.MG_Articoli; -- <--- SOSTITUISCI CON LA TUA TABELLA REALE
GO

-- Vista MOVIMENTI (Mappa i movimenti di magazzino)
CREATE OR ALTER VIEW magazzino.movimenti AS
SELECT 
    IDMovimento         AS id,
    DataMovimento       AS data,
    CodiceArticolo      AS prodotto_codice,
    Causale             AS causale,
    Quantita            AS quantita,
    Segno               AS segno -- '+' o '-'
FROM 
    dbo.MG_Movimenti; -- <--- SOSTITUISCI CON LA TUA TABELLA REALE
GO

-- ============================================================================
-- AGENTE ORDINI
-- ============================================================================

-- Vista ORDINI TESTATA
CREATE OR ALTER VIEW ordini.testata AS
SELECT 
    IDOrdine            AS id,
    NumeroOrdine        AS numero,
    DataOrdine          AS data,
    CodiceCliente       AS cliente_codice,
    RagioneSociale      AS cliente_nome,
    StatoOrdine         AS stato,           -- es. 'Aperto', 'Evaso'
    TotaleOrdine        AS totale
FROM 
    dbo.DOC_Testata -- <--- SOSTITUISCI CON LA TUA TABELLA REALE
WHERE 
    TipoDocumento = 'ORD'; -- Filtra solo gli ordini
GO

-- Vista ORDINI RIGHE
CREATE OR ALTER VIEW ordini.righe AS
SELECT 
    IDRiga              AS id,
    IDOrdine            AS ordine_id,
    CodiceArticolo      AS prodotto_codice,
    Descrizione         AS descrizione,
    Quantita            AS quantita,
    PrezzoUnitario      AS prezzo,
    Sconto              AS sconto,
    TotaleRiga          AS totale
FROM 
    dbo.DOC_Righe; -- <--- SOSTITUISCI CON LA TUA TABELLA REALE
GO

-- ============================================================================
-- AGENTE VENDITE
-- ============================================================================

-- Vista MOVIMENTI (Definita dall'utente)
-- Questa vista unisce dwarehe, anagra, tabcage, artico e tabcfam per analisi complete
CREATE OR ALTER VIEW [vendite].[Movimenti]
AS
SELECT        
    dbo.dwarehe.codditt AS CodiceDitta, 
    dbo.dwarehe.dw_conto AS CodiceCliente, 
    dbo.anagra.an_descr1 AS RagioneSocialeCliente, 
    dbo.dwarehe.dw_codcage AS CodiceAgente, 
    dbo.tabcage.tb_descage AS DescrizioneAgente, 
    dbo.dwarehe.dw_datmov AS DataMovimento, 
    dbo.dwarehe.dw_codart AS CodiceArticolo, 
    dbo.dwarehe.dw_descr AS DescrizioneArticolo, 
    dbo.dwarehe.dw_unmis AS UnitaMisura, 
    dbo.dwarehe.dw_colli AS NumeroColli, 
    dbo.dwarehe.dw_quant AS Quantita, 
    dbo.dwarehe.dw_valore AS ValoreTotale, 
    dbo.dwarehe.dw_vprovv AS ValoreProvvigionale1, 
    dbo.dwarehe.dw_vprovv2 AS ValoreProvvigionale2, 
    dbo.dwarehe.dw_scenario AS Scenario, 
    dbo.dwarehe.dw_anno AS Anno, 
    dbo.tabcfam.tb_codcfam AS [Codice Famiglia], 
    dbo.tabcfam.tb_descfam AS Famiglia
FROM            
    dbo.dwarehe 
    INNER JOIN dbo.anagra ON dbo.dwarehe.codditt = dbo.anagra.codditt AND dbo.dwarehe.dw_conto = dbo.anagra.an_conto 
    INNER JOIN dbo.tabcage ON dbo.dwarehe.codditt = dbo.tabcage.codditt AND dbo.dwarehe.dw_codcage = dbo.tabcage.tb_codcage 
    INNER JOIN dbo.artico ON dbo.dwarehe.codditt = dbo.artico.codditt AND dbo.dwarehe.dw_codart = dbo.artico.ar_codart 
    LEFT OUTER JOIN dbo.tabcfam ON dbo.artico.codditt = dbo.tabcfam.codditt AND dbo.artico.ar_famprod = dbo.tabcfam.tb_codcfam
WHERE        
    (dbo.dwarehe.dw_tipo = 'VEN') AND (dbo.dwarehe.dw_scenario = 1);
GO
