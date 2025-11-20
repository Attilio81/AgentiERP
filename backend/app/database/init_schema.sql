-- =====================================================
-- SQL Server Schema Initialization for Chat AI System
-- =====================================================
-- This script creates the chat_ai schema and all required tables
-- Run this script with sqlcmd or SQL Server Management Studio

USE [YourDatabaseName]; -- TODO: Replace with your actual database name
GO

-- Create schema for chat AI system
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'chat_ai')
BEGIN
    EXEC('CREATE SCHEMA chat_ai');
    PRINT 'Schema chat_ai created successfully';
END
GO

-- =====================================================
-- Users Table
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'chat_ai.users') AND type = 'U')
BEGIN
    CREATE TABLE chat_ai.users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        username NVARCHAR(100) NOT NULL UNIQUE,
        hashed_password NVARCHAR(255) NOT NULL,
        created_at DATETIME2 DEFAULT GETDATE() NOT NULL,
        is_active BIT DEFAULT 1 NOT NULL
    );
    
    CREATE INDEX idx_users_username ON chat_ai.users(username);
    
    PRINT 'Table chat_ai.users created successfully';
END
GO

-- =====================================================
-- Sessions Table
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'chat_ai.sessions') AND type = 'U')
BEGIN
    CREATE TABLE chat_ai.sessions (
        session_id NVARCHAR(64) PRIMARY KEY,
        user_id INT NOT NULL,
        expires_at DATETIME2 NOT NULL,
        created_at DATETIME2 DEFAULT GETDATE() NOT NULL,
        CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) 
            REFERENCES chat_ai.users(id) ON DELETE CASCADE
    );
    
    CREATE INDEX idx_sessions_user_id ON chat_ai.sessions(user_id);
    CREATE INDEX idx_sessions_expires_at ON chat_ai.sessions(expires_at);
    
    PRINT 'Table chat_ai.sessions created successfully';
END
GO

-- =====================================================
-- Conversations Table
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'chat_ai.conversations') AND type = 'U')
BEGIN
    CREATE TABLE chat_ai.conversations (
        id INT IDENTITY(1,1) PRIMARY KEY,
        user_id INT NOT NULL,
        agent_name NVARCHAR(50) NOT NULL,
        title NVARCHAR(200) NULL,
        created_at DATETIME2 DEFAULT GETDATE() NOT NULL,
        updated_at DATETIME2 DEFAULT GETDATE() NOT NULL,
        CONSTRAINT fk_conversations_user FOREIGN KEY (user_id) 
            REFERENCES chat_ai.users(id) ON DELETE CASCADE
    );
    
    CREATE INDEX idx_conversations_user_id ON chat_ai.conversations(user_id);
    CREATE INDEX idx_conversations_agent_name ON chat_ai.conversations(agent_name);
    CREATE INDEX idx_conversations_created_at ON chat_ai.conversations(created_at DESC);
    
    PRINT 'Table chat_ai.conversations created successfully';
END
GO

-- =====================================================
-- Messages Table
-- =====================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'chat_ai.messages') AND type = 'U')
BEGIN
    CREATE TABLE chat_ai.messages (
        id INT IDENTITY(1,1) PRIMARY KEY,
        conversation_id INT NOT NULL,
        role NVARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
        content NVARCHAR(MAX) NOT NULL,
        timestamp DATETIME2 DEFAULT GETDATE() NOT NULL,
        CONSTRAINT fk_messages_conversation FOREIGN KEY (conversation_id) 
            REFERENCES chat_ai.conversations(id) ON DELETE CASCADE
    );
    
    CREATE INDEX idx_messages_conversation_id ON chat_ai.messages(conversation_id);
    CREATE INDEX idx_messages_timestamp ON chat_ai.messages(timestamp);
    
    PRINT 'Table chat_ai.messages created successfully';
END
GO

-- =====================================================
-- Stored Procedure: Cleanup Expired Sessions
-- =====================================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'chat_ai.sp_cleanup_expired_sessions') AND type = 'P')
BEGIN
    DROP PROCEDURE chat_ai.sp_cleanup_expired_sessions;
END
GO

CREATE PROCEDURE chat_ai.sp_cleanup_expired_sessions
AS
BEGIN
    DELETE FROM chat_ai.sessions
    WHERE expires_at < GETDATE();
    
    PRINT CONCAT('Deleted ', @@ROWCOUNT, ' expired sessions');
END
GO

-- =====================================================
-- Verification: List all created objects
-- =====================================================
PRINT '=====================================================';
PRINT 'Schema initialization completed. Objects created:';
PRINT '=====================================================';

SELECT 
    'Schema' AS ObjectType,
    name AS ObjectName
FROM sys.schemas 
WHERE name = 'chat_ai'
UNION ALL
SELECT 
    'Table' AS ObjectType,
    name AS ObjectName
FROM sys.tables 
WHERE schema_id = SCHEMA_ID('chat_ai')
UNION ALL
SELECT 
    'Stored Procedure' AS ObjectType,
    name AS ObjectName
FROM sys.procedures 
WHERE schema_id = SCHEMA_ID('chat_ai')
ORDER BY ObjectType, ObjectName;
GO

PRINT '=====================================================';
PRINT 'IMPORTANT: Update the USE statement at the top of this script';
PRINT 'with your actual database name before running.';
PRINT '=====================================================';
