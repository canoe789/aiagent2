-- Project HELIX v2.0 - Database Schema
-- PostgreSQL initialization script

-- Create database if it doesn't exist (handled by docker-compose)
-- CREATE DATABASE helix;

-- Use the helix database
\c helix;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom ENUM types
CREATE TYPE job_status AS ENUM (
    'PENDING',
    'IN_PROGRESS', 
    'COMPLETED',
    'FAILED',
    'CANCELLED'
);

CREATE TYPE task_status AS ENUM (
    'PENDING',
    'ASSIGNED',
    'IN_PROGRESS',
    'COMPLETED', 
    'FAILED',
    'RETRYING'
);

-- Jobs table - Main user requests
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    status job_status NOT NULL DEFAULT 'PENDING',
    initial_request JSONB NOT NULL,
    session_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);

-- Tasks table - Individual agent tasks
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    agent_id VARCHAR(50) NOT NULL,
    status task_status NOT NULL DEFAULT 'PENDING',
    input_data JSONB NOT NULL DEFAULT '{}',
    output_data JSONB,
    error_log TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    assigned_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Agent prompts table - Versioned AI prompts
CREATE TABLE agent_prompts (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    prompt_text TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    
    -- Ensure only one active prompt per agent
    UNIQUE(agent_id, version),
    CONSTRAINT single_active_prompt_per_agent 
        EXCLUDE (agent_id WITH =) WHERE (is_active = TRUE)
);

-- Artifacts table - Generated content/outputs
CREATE TABLE artifacts (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    schema_id VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure unique artifact names per task
    UNIQUE(task_id, name)
);

-- System logs table - For debugging and monitoring
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    component VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_jobs_session_id ON jobs(session_id) WHERE session_id IS NOT NULL;

CREATE INDEX idx_tasks_job_id ON tasks(job_id);
CREATE INDEX idx_tasks_agent_id ON tasks(agent_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_status_agent ON tasks(status, agent_id);

CREATE INDEX idx_agent_prompts_agent_active ON agent_prompts(agent_id, is_active);

CREATE INDEX idx_artifacts_task_id ON artifacts(task_id);
CREATE INDEX idx_artifacts_name ON artifacts(name);
CREATE INDEX idx_artifacts_schema_id ON artifacts(schema_id);

CREATE INDEX idx_system_logs_component ON system_logs(component);
CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default agent prompts
INSERT INTO agent_prompts (agent_id, version, prompt_text, is_active) VALUES
('AGENT_1', '1.0', 'You are a Creative Director. Transform user requirements into structured creative briefs with clear objectives, target audience, and key messages.', true),
('AGENT_2', '1.0', 'You are a Visual Director. Create detailed visual concepts based on creative briefs, including color schemes, typography, layout, and visual hierarchy.', true),
('AGENT_3', '1.0', 'You are a Frontend Engineer. Generate clean, semantic HTML and modern CSS code based on creative briefs and visual concepts.', true),
('AGENT_4', '1.0', 'You are a QA Compliance Bot. Validate HTML/CSS code for standards compliance, accessibility, and best practices.', true),
('AGENT_5', '1.0', 'You are a Meta-Optimizer. Analyze failed tasks and system performance to propose improvements and optimizations.', true);

-- Create a view for easy task querying
CREATE VIEW pending_tasks AS
SELECT 
    t.id,
    t.job_id,
    t.agent_id,
    t.input_data,
    t.created_at,
    j.initial_request,
    j.session_id
FROM tasks t
JOIN jobs j ON t.job_id = j.id
WHERE t.status = 'PENDING'
ORDER BY t.created_at ASC;

-- Grant permissions (if using specific user)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO helix_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO helix_user;