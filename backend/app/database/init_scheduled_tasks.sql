-- Create scheduled_tasks table in chat_ai schema
-- This table stores automated task schedules for running agent queries and sending email reports

IF NOT EXISTS (SELECT * FROM sys.tables t 
               JOIN sys.schemas s ON t.schema_id = s.schema_id 
               WHERE s.name = 'chat_ai' AND t.name = 'scheduled_tasks')
BEGIN
    CREATE TABLE chat_ai.scheduled_tasks (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(200) NOT NULL,
        description NVARCHAR(500) NULL,
        agent_name NVARCHAR(50) NOT NULL,
        prompt NVARCHAR(MAX) NOT NULL,
        cron_expression NVARCHAR(100) NOT NULL,
        recipient_emails NVARCHAR(MAX) NOT NULL, -- JSON array of email addresses
        is_active BIT NOT NULL DEFAULT 1,
        last_run_at DATETIME NULL,
        next_run_at DATETIME NULL,
        last_run_status NVARCHAR(50) NULL, -- 'success', 'failed', 'pending'
        last_run_error NVARCHAR(MAX) NULL,
        created_by_user_id INT NOT NULL,
        created_at DATETIME NOT NULL DEFAULT GETDATE(),
        updated_at DATETIME NOT NULL DEFAULT GETDATE(),
        
        CONSTRAINT FK_scheduled_tasks_user FOREIGN KEY (created_by_user_id) 
            REFERENCES chat_ai.users(id) ON DELETE CASCADE,
        CONSTRAINT CHK_scheduled_tasks_active CHECK (is_active IN (0, 1))
    );

    -- Create indexes for better query performance
    CREATE INDEX IX_scheduled_tasks_is_active ON chat_ai.scheduled_tasks(is_active);
    CREATE INDEX IX_scheduled_tasks_next_run_at ON chat_ai.scheduled_tasks(next_run_at);
    CREATE INDEX IX_scheduled_tasks_agent_name ON chat_ai.scheduled_tasks(agent_name);
    CREATE INDEX IX_scheduled_tasks_created_by ON chat_ai.scheduled_tasks(created_by_user_id);

    PRINT 'Table chat_ai.scheduled_tasks created successfully.';
END
ELSE
BEGIN
    PRINT 'Table chat_ai.scheduled_tasks already exists.';
END
GO
