-- Connect to HRAnalyticsDB (use lowercase as PostgreSQL converts to lowercase)
\c hranalyticsdb;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS "pgvector"; -- Uncomment after installing pgvector

-- Create compensation schema
CREATE SCHEMA IF NOT EXISTS compensation;

-- Set search path
SET search_path TO compensation, public;

-- Create benchmarks table for Mercer and other market data
CREATE TABLE IF NOT EXISTS compensation.benchmarks (
    id UUID DEFAULT uuid_generate_v4(),
    source_type VARCHAR(50) NOT NULL, -- 'mercer', 'lattice', 'glassdoor'
    source_file VARCHAR(255),
    job_family VARCHAR(100),
    job_code VARCHAR(50),
    job_title VARCHAR(255),
    level INTEGER,
    band INTEGER,
    zone INTEGER,
    geography VARCHAR(255),
    location VARCHAR(255),
    market_segment VARCHAR(100),
    industry VARCHAR(100),
    company_count INTEGER,
    employee_count INTEGER,

    -- Compensation percentiles
    p10_salary DECIMAL(12,2),
    p25_salary DECIMAL(12,2),
    p50_salary DECIMAL(12,2),
    p75_salary DECIMAL(12,2),
    p90_salary DECIMAL(12,2),
    mean_salary DECIMAL(12,2),

    -- Market indicators
    trend_indicator VARCHAR(50),
    trend_velocity VARCHAR(20),

    -- Metadata
    data_date DATE,
    currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,

    -- Metadata
    CONSTRAINT benchmarks_pkey_constraint PRIMARY KEY (id)
);

-- Create salary_ranges table for calculated ranges
CREATE TABLE IF NOT EXISTS compensation.salary_ranges (
    id UUID DEFAULT uuid_generate_v4(),
    job_analysis_id UUID,
    job_title VARCHAR(255) NOT NULL,
    job_family VARCHAR(100),
    level INTEGER,
    band INTEGER,
    zone INTEGER,
    location VARCHAR(255),

    -- Experience requirements
    years_experience_min INTEGER,
    years_experience_max INTEGER,

    -- Base salary ranges
    base_salary_min DECIMAL(12,2),
    base_salary_p25 DECIMAL(12,2),
    base_salary_p50 DECIMAL(12,2),
    base_salary_p75 DECIMAL(12,2),
    base_salary_max DECIMAL(12,2),

    -- Total compensation
    total_comp_min DECIMAL(12,2),
    total_comp_target DECIMAL(12,2),
    total_comp_max DECIMAL(12,2),

    -- Adjustments
    geographic_factor DECIMAL(5,3) DEFAULT 1.0,
    market_adjustment DECIMAL(5,3) DEFAULT 1.0,
    skills_premium DECIMAL(5,3) DEFAULT 0.0,

    -- Final recommendations
    recommended_min DECIMAL(12,2),
    recommended_target DECIMAL(12,2),
    recommended_max DECIMAL(12,2),

    -- Data sources used
    data_sources JSONB,
    confidence_score DECIMAL(3,2),

    -- AI Analysis
    openai_analysis JSONB,
    ai_justification TEXT,
    market_insights JSONB,

    -- Metadata
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP,
    approved_by VARCHAR(255),

    -- Primary key constraint
    CONSTRAINT salary_ranges_pkey_constraint PRIMARY KEY (id)
);

-- Create job_analyses table for storing parsed job descriptions
CREATE TABLE IF NOT EXISTS compensation.job_analyses (
    id UUID DEFAULT uuid_generate_v4(),

    -- Job information
    job_title VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    raw_description TEXT,

    -- Parsed data
    parsed_data JSONB NOT NULL,
    openai_analysis JSONB,
    -- embedding vector(1536), -- Uncomment after installing pgvector
    embedding TEXT,

    -- Classification
    detected_level INTEGER,
    detected_band INTEGER,
    zone INTEGER,
    location VARCHAR(255),
    remote_type VARCHAR(50), -- 'onsite', 'hybrid', 'remote'

    -- Requirements
    years_experience_min INTEGER,
    years_experience_max INTEGER,
    skills_extracted JSONB,
    education_requirements JSONB,
    certifications JSONB,

    -- Organization
    job_family VARCHAR(100),
    department VARCHAR(100),
    reports_to VARCHAR(255),
    team_size INTEGER,

    -- Analysis metadata
    confidence_score DECIMAL(3,2),
    analysis_version VARCHAR(20),

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    analyzed_at TIMESTAMP,

    -- Primary key constraint
    CONSTRAINT job_analyses_pkey_constraint PRIMARY KEY (id)
);

-- Create conversations table for chat history
CREATE TABLE IF NOT EXISTS compensation.conversations (
    id UUID DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    job_analysis_id UUID REFERENCES compensation.job_analyses(id),

    -- Conversation data
    messages JSONB DEFAULT '[]'::jsonb,
    openai_thread_id VARCHAR(255),

    -- Usage tracking
    total_tokens_used INTEGER DEFAULT 0,
    total_cost_usd DECIMAL(10,6) DEFAULT 0,

    -- Context
    context JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_message_at TIMESTAMP,

    -- Primary key constraint
    CONSTRAINT conversations_pkey_constraint PRIMARY KEY (id)
);

-- Create OpenAI cache table
CREATE TABLE IF NOT EXISTS compensation.openai_cache (
    id UUID DEFAULT uuid_generate_v4(),
    prompt_hash VARCHAR(64) UNIQUE NOT NULL,
    model VARCHAR(50),
    prompt TEXT,
    response JSONB,
    tokens_used INTEGER,
    cost_usd DECIMAL(10,6),
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,

    -- Primary key constraint
    CONSTRAINT openai_cache_pkey_constraint PRIMARY KEY (id)
);

-- Create audit log table
CREATE TABLE IF NOT EXISTS compensation.audit_logs (
    id UUID DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),

    -- Primary key constraint
    CONSTRAINT audit_logs_pkey_constraint PRIMARY KEY (id)
);

-- Create users table for authentication
CREATE TABLE IF NOT EXISTS compensation.users (
    id UUID DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    password_hash VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Primary key constraint
    CONSTRAINT users_pkey_constraint PRIMARY KEY (id)
);

-- Grant permissions
GRANT ALL ON SCHEMA compensation TO admin;
GRANT ALL ON ALL TABLES IN SCHEMA compensation TO admin;
GRANT ALL ON ALL SEQUENCES IN SCHEMA compensation TO admin;

-- Create update trigger for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at
CREATE TRIGGER update_benchmarks_updated_at BEFORE UPDATE ON compensation.benchmarks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_salary_ranges_updated_at BEFORE UPDATE ON compensation.salary_ranges
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_analyses_updated_at BEFORE UPDATE ON compensation.job_analyses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON compensation.conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON compensation.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();